#!/usr/bin/env python
### Utility functions

def eq(x, y):
    if x == 'not so sure':
        return False
    return x == y

### Rules and initial conditions

def define_ctxs(sh):
    sh.define_ctx(Ctx('patient', ['name', 'sex', 'age']))
    sh.define_ctx(Ctx('disease', goals=['identity']))

def patient_yes_no(sh,param):
    sh.define_param(Param(param, 'patient', enum=['no', 'yes', 'not so sure']))

def disease_rule(sh,rule,precondition,symptom,disease,certainty):
    sh.define_rule(Rule(rule,
        [(precondition, 'patient', eq, 'yes'),
         (symptom, 'patient', eq, 'yes')],
        [('identity', 'disease', eq, disease)],
        certainty))

def pregnancy(sh,rule,precondition,symptom,certainty):
    sh.define_rule(Rule(rule,
        [('sex','patient',eq,'f'),
         (precondition, 'patient', eq, 'yes'),
         (symptom, 'patient', eq, 'yes')],
        [('identity', 'disease', eq, 'pregnancy')],
        certainty))

def define_params(sh):
    # Patient params
    sh.define_param(Param('name', 'patient', cls=str, ask_first=True))
    sh.define_param(Param('sex', 'patient', enum=['m', 'f'], ask_first=True))
    sh.define_param(Param('age', 'patient', cls=int, ask_first=True))
    patient_yes_no(sh,'respiratory issues')
    patient_yes_no(sh,'mental issues')
    patient_yes_no(sh,'eye issues')
    patient_yes_no(sh,'skin issues')
    patient_yes_no(sh,'pain issues')
    patient_yes_no(sh,'sensory issues')
    patient_yes_no(sh,'sleep issues')
    patient_yes_no(sh,'digestive issues')
    patient_yes_no(sh,'bleeding')
    patient_yes_no(sh,'breathing-problems')
    patient_yes_no(sh,'itchy-eyes')
    patient_yes_no(sh,'conjunctivitis')
    patient_yes_no(sh,'coughing')
    patient_yes_no(sh,'diarrhea')
    patient_yes_no(sh,'headache')
    patient_yes_no(sh,'hives')
    patient_yes_no(sh,'itching')
    patient_yes_no(sh,'cramps')
    patient_yes_no(sh,'runny-nose')
    patient_yes_no(sh,'rashes')
    patient_yes_no(sh,'vomiting')
    patient_yes_no(sh,'wheezing')
    patient_yes_no(sh,'concentration-problems')
    patient_yes_no(sh,'fatigue')
    patient_yes_no(sh,'irritability')
    patient_yes_no(sh,'sleep-issues')
    patient_yes_no(sh,'restlessness')
    patient_yes_no(sh,'chest-pain')
    patient_yes_no(sh,'confusion')
    patient_yes_no(sh,'tinnitus')
    patient_yes_no(sh,'nosebleed')
    patient_yes_no(sh,'vision-issues')
    patient_yes_no(sh,'body-aches')
    patient_yes_no(sh,'muscle-pain')
    patient_yes_no(sh,'ibs')
    patient_yes_no(sh,'memory-difficulties')
    patient_yes_no(sh,'numbness')
    patient_yes_no(sh,'palpitations')
    patient_yes_no(sh,'sleep-disturbances')
    patient_yes_no(sh,'migraines')
    patient_yes_no(sh,'yeast-infections')
    patient_yes_no(sh,'mouth-sores')
    patient_yes_no(sh,'sore-throat')
    patient_yes_no(sh,'swollen-glands')
    patient_yes_no(sh,'distended abdomen')
    patient_yes_no(sh,'breast tenderness')
    patient_yes_no(sh,'light-headed')
    patient_yes_no(sh,'missed-period')
    patient_yes_no(sh,'nausea')
    patient_yes_no(sh,'frequent-urination')

    # disease params
    diseases = ['allergies', 'generalized anxiety disorder', 'fibromyalgia',
                 'hypertension', 'HIV infection', 'pregnancy']

def define_rules(sh):
    # Respiratory rules
    disease_rule(sh, 1, 'respiratory issues', 'breathing-problems','allergies',0.4)
    disease_rule(sh, 2, 'respiratory issues', 'coughing','allergies', 0.2)
    disease_rule(sh, 3, 'respiratory issues', 'runny-nose','allergies', 0.4)
    disease_rule(sh, 4, 'respiratory issues', 'wheezing','allergies', 0.1)
    disease_rule(sh, 5, 'respiratory issues', 'palpitations','fibromyalgia', 0.1)
    pregnancy(sh, 6, 'respiratory issues', 'light-headed', 0.3)

    # Eye rules
    disease_rule(sh, 7, 'eye issues', 'itchy-eyes','allergies', 0.4)
    disease_rule(sh, 8, 'eye issues', 'conjunctivitis','allergies', 0.3)

    # Digestive rules
    disease_rule(sh, 9, 'digestive issues', 'diarrhea','allergies', -0.3)
    disease_rule(sh, 10, 'digestive issues', 'cramps','allergies', -0.1)
    disease_rule(sh, 11, 'digestive issues', 'vomiting','allergies', -0.1)
    disease_rule(sh, 12, 'digestive issues', 'ibs','fibromyalgia', -0.1)
    disease_rule(sh, 13, 'digestive issues', 'diarrhea','HIV infection', 0.3)
    pregnancy(sh, 14, 'digestive issues', 'nausea', 0.3)
    pregnancy(sh, 15, 'digestive issues', 'frequent urination', 0.3)


    # Pain rules
    disease_rule(sh, 16, 'pain issues', 'headache','allergies', 0.0)
    disease_rule(sh, 17, 'pain issues', 'chest-pain','hypertension', 0.5)
    disease_rule(sh, 18, 'pain issues', 'body-aches','fibromyalgia', 0.2)
    disease_rule(sh, 19, 'pain issues', 'muscle-pain','fibromyalgia', 0.2)
    disease_rule(sh, 20, 'pain issues', 'numbness','fibromyalgia', 0.2)
    disease_rule(sh, 21, 'pain issues', 'migraines','fibromyalgia', 0.2)
    disease_rule(sh, 22, 'pain issues', 'mouth-sores','HIV infection', 0.6)
    disease_rule(sh, 23, 'pain issues', 'muscle-pain','HIV infection', 0.2)
    disease_rule(sh, 24, 'pain issues', 'sore-throat','HIV infection', 0.2)
    disease_rule(sh, 25, 'pain issues', 'swollen-glands','HIV infection', 0.2)
    pregnancy(sh, 26, 'pain issues', 'breast tenderness', 0.1)

    # Skin rules
    disease_rule(sh, 27, 'skin issues', 'hives','allergies', 0.7)
    disease_rule(sh, 28, 'skin issues', 'itching','allergies', 0.2)
    disease_rule(sh, 29, 'skin issues', 'rashes','allergies', 0.2)
    disease_rule(sh, 30, 'skin issues', 'fever','HIV infection', 0.2)
    disease_rule(sh, 31, 'skin issues', 'yeast-infections','HIV infection', 0.4)
    disease_rule(sh, 32, 'skin issues', 'rashes','HIV infection', 0.4)
    pregnancy(sh, 33, 'skin issues', 'distended abdomen', 0.9)

    # Mental rules
    disease_rule(sh, 34, 'mental issues', 'concentration-problems','generalized anxiety disorder', 0.5)
    disease_rule(sh, 35, 'mental issues', 'irritability','generalized anxiety disorder', 0.5)
    disease_rule(sh, 36, 'mental issues', 'confusion','hypertension', 0.0)
    disease_rule(sh, 37, 'mental issues', 'memory-difficulties','fibromyalgia', 0.0)

    # Sleep rules
    disease_rule(sh, 38, 'sleep issues', 'fatigue','generalized anxiety disorder', 0.0)
    disease_rule(sh, 39, 'sleep issues', 'sleep-issues','generalized anxiety disorder', 0.7)
    disease_rule(sh, 40, 'sleep issues', 'restlessness','generalized anxiety disorder', 0.3)
    disease_rule(sh, 41, 'sleep issues', 'fatigue','hypertension', 0.3)
    disease_rule(sh, 42, 'sleep issues', 'sleep-issues','fibromyalgia', 0.3)

    # Sensory rules
    disease_rule(sh, 43, 'sensory issues', 'tinnitus','hypertension', 0.5)
    disease_rule(sh, 44, 'sensory issues', 'vision-issues','hypertension', 0.3)

    # Bleeding rules
    disease_rule(sh, 45, 'bleeding', 'nosebleed','hypertension', 0.7)
    pregnancy(sh, 46, 'bleeding', 'missed-period', 0.7)


### Running the system

from shell import Param, Ctx, Rule, Shell

def report_findings(findings):
    for inst, result in findings.items():
        print 'Findings for %s-%d:' % (inst[0], inst[1])
        for param, vals in result.items():
            possibilities = ['%s: %f' % (val[0], val[1]) for val in vals.items()]
            print '%s: %s' % (param, ', '.join(possibilities))
        
def main():
    sh = Shell()
    define_ctxs(sh)
    define_params(sh)
    define_rules(sh)
    report_findings(sh.execute(['patient', 'disease']))

main()
