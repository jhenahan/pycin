# A few utilities for dealing with certainty judgments

def cert_or(a, b):
    if a > 0 and b > 0:
        return a + b - a * b
    elif a < 0 and b < 0:
        return a + b + a * b
    else:
        return (a + b) / (1 - min(abs(a), abs(b)))

def cert_and(a, b):
    return min(a, b)

def is_cert(x):
    return Cert.false <= x <= Cert.true

def cert_true(x):
    return is_cert(x) and x > Cert.cutoff

def cert_false(x):
    return is_cert(x) and x < (Cert.cutoff - 1)

class Cert(object):
    true = 1.0
    false = -1.0
    unknown = 0.0
    cutoff = 0.2

# Context (the things we can reason about)

class Ctx(object):
    def __init__(self, name, initial=None, goals=None):
        self.count = 0
        self.name = name
        self.initial = initial or []
        self.goals = goals or []
    
    def build(self):
        inst = (self.name, self.count)
        self.count += 1
        return inst

# Parameters (the qualities of the context that we're interested in)

class Param(object):
    def __init__(self, name, ctx=None, enum=None, cls=None, ask_first=False):
        self.name = name
        self.ctx = ctx
        self.enum = enum
        self.ask_first = ask_first
        self.cls = cls
        
    def type_string(self):
        return self.cls.__name__ if self.cls else '(%s)' % ', '.join(list(self.enum))
    
    def from_string(self, val):
        if self.cls:
            return self.cls(val)
        if self.enum and val in self.enum:
            return val
        
        raise ValueError('val must be one of %s for the param %s' %
                         (', '.join(list(self.enum)), self.name))

def eval_condition(condition, values, discover=None):
    param, inst, op, val = condition
    if discover:
        discover(param, inst)
    total = sum(cert for given_val, cert in values.items() if op(given_val, val))
    
    return total

def print_condition(condition):
    param, inst, op, val = condition
    name = inst if isinstance(inst, str) else inst[0]
    opname = op.__name__
    return '%s %s %s %s' % (param, name, opname, val)

def get_vals(values, param, inst):
    return values.setdefault((param, inst), {})

def get_cert(values, param, inst, val):
    vals = get_vals(values, param, inst)
    return vals.setdefault(val, Cert.unknown)

def update_cert(values, param, inst, val, cert):
    existing = get_cert(values, param, inst, val)
    updated = cert_or(existing, cert)
    get_vals(values, param, inst)[val] = updated
    

# Rules (how we reason about the context)

class Rule(object):
    def __init__(self, num, premises, conclusions, cert):
        self.num = num
        self.cert = cert
        self.raw_premises = premises 
        self.raw_conclusions = conclusions
    
    def __str__(self):
        prems = map(print_condition, self.raw_premises)
        concls = map(print_condition, self.raw_conclusions)
        templ = 'RULE %d\nIF\n\t%s\nTHEN %f\n\t%s'
        return templ % (self.num, '\n\t'.join(prems), self.cert, '\n\t'.join(concls))
    
    def clone(self):
        return Rule(self.num, list(self.raw_premises),
                    list(self.raw_conclusions), self.cert)
    
    def _bind_cond(self, cond, instances):
        param, ctx, op, val = cond
        return param, instances[ctx], op, val
        
    def premises(self, instances):
        return [self._bind_cond(premise, instances) for premise in self.raw_premises]
    
    def conclusions(self, instances):
        return [self._bind_cond(concl, instances) for concl in self.raw_conclusions]

    def applicable(self, values, instances, discover=None):
        for premise in self.premises(instances):
            param, inst, op, val = premise
            vals = get_vals(values, param, inst)
            cert = eval_condition(premise, vals)
            if cert_false(cert):
                return Cert.false
                        
        total_cert = Cert.true
        for premise in self.premises(instances):
            param, inst, op, val = premise
            vals = get_vals(values, param, inst)
            cert = eval_condition(premise, vals, discover)
            total_cert = cert_and(total_cert, cert)
            if not cert_true(total_cert):
                return Cert.false
        return total_cert

    def apply(self, values, instances, discover=None, track=None):
        
        if track:
            track(self)
        
        cert = self.cert * self.applicable(values, instances, discover)
        if not cert_true(cert):
            return False
        
        for conclusion in self.conclusions(instances):
            param, inst, op, val = conclusion
            update_cert(values, param, inst, val, cert)
        
        return True


def use_rules(values, instances, rules, discover=None, track_rules=None):
    
    return any([rule.apply(values, instances, discover, track_rules) for rule in rules])


def write(line): print line

# The Expert Shell (how we interact with the rule system)

class Shell(object):
    
    def __init__(self, read=raw_input, write=write):
        self.read = read
        self.write = write
        self.rules = {}
        self.ctxs = {}
        self.params = {}
        self.given = set()
        self.asked = set()
        self.given_values = {}
        self.current_inst = None
        self.instances = {}
        self.current_rule = None
    
    def clear(self):
        self.given.clear()
        self.asked.clear()
        self.given_values.clear()
        self.current_inst = None
        self.current_rule = None
        self.instances.clear()
    
    def define_rule(self, rule):
        for param, ctx, op, val in rule.raw_conclusions:
            self.rules.setdefault(param, []).append(rule)
    
    def define_ctx(self, ctx):
        self.ctxs[ctx.name] = ctx
        
    def define_param(self, param):
        self.params[param.name] = param
    
    def get_rules(self, param):
        return self.rules.setdefault(param, [])
    
    def build(self, ctx_name):
        inst = self.ctxs[ctx_name].build()
        self.current_inst = inst
        self.instances[ctx_name] = inst
        return inst
    
    def get_param(self, name):
        return self.params.setdefault(name, Param(name))
    
    HELP = """Type one of the following:
?       - to see possible answers for this param
rule    - to show the current rule
why     - to see why this question is asked
help    - to show this message
unknown - if the answer to this question is not given
<val>   - a single definite answer to the question
<val1> <cert1> [, <val2> <cert2>, ...]
        - if there are multiple answers with associated certainty factors."""

    def ask_values(self, param, inst):
        
        if (param, inst) in self.asked:
            return

        self.asked.add((param, inst))
        while True:
            resp = self.read('%s? ' % (param))
            if not resp:
                continue
            if resp == 'unknown':
                return False
            elif resp == 'help':
                self.write(Shell.HELP)
            elif resp == 'why':
                self.print_why(param)
            elif resp == 'rule':
                self.write(self.current_rule)
            elif resp == '?':
                self.write('%s must be of type %s' %
                           (param, self.get_param(param).type_string()))
            else:
                try:
                    for val, cert in parse_reply(self.get_param(param), resp):
                        update_cert(self.given_values, param, inst, val, cert)
                    return True
                except:
                    self.write('Invalid response. Type ? to see legal ones.')
    
    def print_why(self, param):
        self.write('Why is the value of %s being asked for?' % param)
        if self.current_rule in ('initial', 'goal'):
            self.write('%s is one of the %s params.' % (param, self.current_rule))
            return

        given, unknown = [], []
        for premise in self.current_rule.premises(self.instances):
            vals = get_vals(self.given_values, premise[0], premise[1])
            if cert_true(eval_condition(premise, vals)):
                given.append(premise)
            else:
                unknown.append(premise)
        
        if given:
            self.write('It is given that:')
            for condition in given:
                self.write(print_condition(condition))
            self.write('Therefore,')
        
        rule = self.current_rule.clone()
        rule.raw_premises = unknown
        self.write(rule)
    
    def _set_current_rule(self, rule):
        self.current_rule = rule
    
    def discover(self, param, inst=None):
        inst = inst or self.current_inst

        if (param, inst) in self.given: 
            return True
        
        def rules():
            return use_rules(self.given_values, self.instances,
                             self.get_rules(param), self.discover,
                             self._set_current_rule)

        if self.get_param(param).ask_first:
            success = self.ask_values(param, inst) or rules()
        else:
            success = rules() or self.ask_values(param, inst)
        if success:
            self.given.add((param, inst)) 
        return success

    def execute(self, ctx_names):
        self.write('CS 251 - Final Project. Jack Henahan. For help answering questions, type "help".')
        self.clear()
        results = {}
        for name in ctx_names:
            ctx = self.ctxs[name]
            self.build(name)
            
            self._set_current_rule('initial')
            for param in ctx.initial:
                self.discover(param)
            
            self._set_current_rule('goal')
            for param in ctx.goals:
                self.discover(param)
            
            if ctx.goals:
                result = {}
                for param in ctx.goals:
                    result[param] = get_vals(self.given_values, param, self.current_inst)
                results[self.current_inst] = result
            
        return results

def parse_reply(param, reply):
    if reply.find(',') >= 0:
        vals = []
        for pair in reply.split(','):
            val, cert = pair.strip().split(' ')
            vals.append((param.from_string(val), float(cert)))
        return vals
    return [(param.from_string(reply), Cert.true)]


