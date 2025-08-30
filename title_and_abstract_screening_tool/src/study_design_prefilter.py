"""
Study Design Prefilter Module
Used for high-specificity keyword-based study design identification before LLM screening
"""

class StudyDesignPrefilter:    
    def __init__(self):

        self.design_hierarchy = {
            "review": [
                "systematic_review", "narrative_review", "scoping_review", 
                "literature_review", "overview", "umbrella_review", "critical_review",
                "integrative_review", "state_of_the_art_review", "clinical_review"
            ],
            "systematic_review": ["meta_analysis", "network_meta_analysis"],
            
            "observational_study": [
                "cohort_study", "case_control_study", "cross_sectional_study",
                "longitudinal_study", "retrospective_study", "prospective_study",
                "ecological_study", "registry_study", "population_study"
            ],

            "experimental_study": [
                "randomized_controlled_trial", "non_randomized_trial", 
                "quasi_experimental_study", "pragmatic_trial",
                "pilot_study", "feasibility_study", "clinical_trial"
            ],

            "qualitative_study": [
                "interview_study", "focus_group_study", "ethnography",
                "phenomenological_study", "grounded_theory_study", "case_study_qualitative"
            ],

            "case_study": ["case_report", "case_series"],

            "survey_study": ["questionnaire_study", "delphi_study"],

            "economic_study": ["cost_effectiveness_analysis", "cost_utility_analysis", "budget_impact_analysis"],
            "mixed_methods_study": [],

            "non_formal_study": [
                "protocol", "erratum", "letter", "comment", "commentary", "editorial", "perspective", "opinion", "correspondence"
            ]
        }

        self.title_high_specificity_keywords = {
            "systematic_review": [
                ": a systematic review", ": systematic review", "- systematic review",
                ": a systematic literature review", ": systematic literature review",
                "- systematic literature review", ": a systematic narrative review",
                ": systematic review and", "- systematic review and",
                ": a systematic review and", "- a systematic review and",
                "systematic review of", "systematic review on",
                ": findings from a systematic review", "- findings from a systematic review",
                ": results from a systematic review", "- results from a systematic review",
                ": results of a systematic review", "- results of a systematic review",
                ": protocol for a systematic review", "- protocol for a systematic review",
                ": protocol of a systematic review", "- protocol of a systematic review",
                "systematic approach to review", "systematically reviewed literature",
                ": an updated systematic review", "- an updated systematic review",
                ": systematic analysis", "- systematic analysis"
            ],
            
            "meta_analysis": [
                ": a meta-analysis", ": meta-analysis", "- meta-analysis",
                ": a metaanalysis", ": metaanalysis", "- metaanalysis",
                ": a meta analysis", ": meta analysis", "- meta analysis", 
                ": a meta-analytic review", ": meta-analytic review", "- meta-analytic review",
                ": a systematic review and meta-analysis", "- a systematic review and meta-analysis",
                ": systematic review and meta-analysis", "- systematic review and meta-analysis",
                "meta-analysis of", "metaanalysis of", "meta analysis of",
                "pooled meta-analysis", "pooled meta analysis",
                ": an updated meta-analysis", "- an updated meta-analysis",
                ": results from a meta-analysis", "- results from a meta-analysis",
                ": results of a meta-analysis", "- results of a meta-analysis",
                ": findings from a meta-analysis", "- findings from a meta-analysis",
                ": findings of a meta-analysis", "- findings of a meta-analysis"
            ],
            
            "network_meta_analysis": [
                ": a network meta-analysis", ": network meta-analysis", "- network meta-analysis",
                ": a network metaanalysis", ": network metaanalysis", "- network metaanalysis",
                ": a network meta analysis", ": network meta analysis", "- network meta analysis",
                ": a network pooling analysis", ": network pooling analysis", "- network pooling analysis",
                "network meta-analysis of", "network metaanalysis of", "network meta analysis of",
                "bayesian network meta-analysis", "frequentist network meta-analysis",
                "mixed-effects network meta-analysis",
                ": a bayesian network meta-analysis", ": bayesian network meta-analysis",
                ": a mixed treatment comparison", ": mixed treatment comparison",
                "- mixed treatment comparison", "mixed treatment comparison of",
                ": a multiple treatment meta-analysis", ": multiple treatment meta-analysis",
                "- multiple treatment meta-analysis", "multiple treatment meta-analysis of",
                ": a systematic review and network meta-analysis", "- a systematic review and network meta-analysis",
                ": systematic review and network meta-analysis", "- systematic review and network meta-analysis"
            ],
            
            "narrative_review": [
                ": a narrative review", ": narrative review", "- narrative review",
                "narrative review of", "narrative review on",
                ": a narrative literature review", ": narrative literature review",
                "- narrative literature review", "narrative literature review of",
                ": a comprehensive narrative review", ": comprehensive narrative review",
                "- comprehensive narrative review"
            ],
            
            "scoping_review": [
                ": a scoping review", ": scoping review", "- scoping review",
                "scoping review of", "scoping review on",
                ": a scoping literature review", ": scoping literature review",
                "- scoping literature review", ": protocol for a scoping review",
                "- protocol for a scoping review", ": results of a scoping review",
                "- results of a scoping review", ": findings from a scoping review",
                "- findings from a scoping review"
            ],
            
            "literature_review": [
                "a review", "review of", "review on", "review of", "review on", "review article", "review paper",
                ": a literature review", ": literature review", "- literature review",
                "literature review of", "literature review on", "literature review:",
                ": a critical literature review", ": critical literature review", 
                "- critical literature review", ": a comprehensive literature review", 
                ": comprehensive literature review", "- comprehensive literature review"
            ],
            
            "overview": [
                ": an overview", ": overview", "- overview",
                ": an overview of", "overview of", "overview on",
                ": a comprehensive overview", ": comprehensive overview",
                "- comprehensive overview", ": a critical overview",
                ": critical overview", "- critical overview"
            ],

            "umbrella_review": [
                ": an umbrella review", ": umbrella review", "- umbrella review",
                "umbrella review of", "umbrella review on",
                ": an umbrella systematic review", ": umbrella systematic review",
                "- umbrella systematic review"
            ],

            "critical_review": [
                ": a critical review", ": critical review", "- critical review",
                "critical review of", "critical review on",
                ": a critical analysis", ": critical analysis", "- critical analysis"
            ],

            "integrative_review": [
                ": an integrative review", ": integrative review", "- integrative review",
                "integrative review of", "integrative review on",
                ": an integrated review", ": integrated review", "- integrated review"
            ],

            "state_of_the_art_review": [
                ": a state-of-the-art review", ": state-of-the-art review", 
                "- state-of-the-art review", ": state of the art review", 
                "- state of the art review", "state-of-the-art review of", 
                "state of the art review of"
            ],

            "clinical_review": [
                ": a clinical review", ": clinical review", "- clinical review",
                "clinical review of", "clinical review on"
            ],
            
            "cohort_study": [
                ": a cohort study", ": cohort study", "- cohort study", 
                ": a cohort analysis", ": cohort analysis", "- cohort analysis",
                "cohort study of", "cohort study on", "cohort analysis of",
                ": a prospective cohort study", ": prospective cohort study", "- prospective cohort study",
                ": a retrospective cohort study", ": retrospective cohort study", "- retrospective cohort study",
                ": a population-based cohort study", ": population-based cohort study", "- population-based cohort study",
                ": a multicenter cohort study", ": multicenter cohort study", "- multicenter cohort study",
                ": a nationwide cohort study", ": nationwide cohort study", "- nationwide cohort study",
                ": a large cohort study", ": large cohort study", "- large cohort study",
                ": a longitudinal cohort study", ": longitudinal cohort study", "- longitudinal cohort study",
                ": a multinational cohort study", ": multinational cohort study", "- multinational cohort study",
                ": an ambidirectional cohort study", ": ambidirectional cohort study", "- ambidirectional cohort study",
                ": a historical cohort study", ": historical cohort study", "- historical cohort study",
                "findings from a cohort study", "results from a cohort study"
            ],

            "case_control_study": [
                ": a case-control study", ": case-control study", "- case-control study",
                ": a case control study", ": case control study", "- case control study",
                ": a matched case-control study", ": matched case-control study", "- matched case-control study",
                ": a nested case-control study", ": nested case-control study", "- nested case-control study",
                ": a population-based case-control study", ": population-based case-control study",
                "- population-based case-control study", "case-control analysis", "case control analysis",
                "case-control study of", "case-control study on", "case control study of",
                "findings from a case-control study", "results from a case-control study"
            ],
            
            "cross_sectional_study": [
                ": a cross-sectional study", ": cross-sectional study", "- cross-sectional study",
                ": a cross sectional study", ": cross sectional study", "- cross sectional study",
                ": a population-based cross-sectional study", ": population-based cross-sectional study",
                "- population-based cross-sectional study", "cross-sectional analysis",
                "cross sectional analysis", "cross-sectional survey", "cross sectional survey",
                "cross-sectional study of", "cross-sectional study on", "cross sectional study of",
                "findings from a cross-sectional study", "results from a cross-sectional study"
            ],
            
            "longitudinal_study": [
                ": a longitudinal study", ": longitudinal study", "- longitudinal study",
                "longitudinal study of", "longitudinal study on", "longitudinal analysis",
                ": a longitudinal analysis", ": longitudinal analysis", "- longitudinal analysis",
                ": a prospective longitudinal study", ": prospective longitudinal study",
                "- prospective longitudinal study", "findings from a longitudinal study",
                "results from a longitudinal study"
            ],

            "retrospective_study": [
                ": a retrospective study", ": retrospective study", "- retrospective study",
                ": a retrospective analysis", ": retrospective analysis", "- retrospective analysis",
                ": a retrospective observational study", ": retrospective observational study",
                "- retrospective observational study", ": a retrospective chart review",
                ": retrospective chart review", "- retrospective chart review",
                "retrospective study of", "retrospective study on", "retrospective analysis of",
                "findings from a retrospective study", "results from a retrospective study"
            ],

            "prospective_study": [
                ": a prospective study", ": prospective study", "- prospective study",
                ": a prospective analysis", ": prospective analysis", "- prospective analysis",
                ": a prospective observational study", ": prospective observational study",
                "- prospective observational study", ": a prospective evaluation",
                ": prospective evaluation", "- prospective evaluation",
                "prospective study of", "prospective study on", "prospective analysis of",
                "findings from a prospective study", "results from a prospective study"
            ],

            "ecological_study": [
                ": an ecological study", ": ecological study", "- ecological study",
                ": an ecologic study", ": ecologic study", "- ecologic study", 
                "ecological analysis", "ecologic analysis", "ecological comparison",
                "ecological study of", "ecological study on", "ecologic study of"
            ],

            "registry_study": [
                ": a registry study", ": registry study", "- registry study",
                ": a registry-based study", ": registry-based study", "- registry-based study",
                ": a registry analysis", ": registry analysis", "- registry analysis",
                "registry study of", "registry study on", "registry analysis of",
                ": results from a registry", "- results from a registry",
                "findings from a registry"
            ],

            "population_study": [
                ": a population-based study", ": population-based study", "- population-based study", 
                ": a population study", ": population study", "- population study",
                "population-based analysis", "population study of", "population study on",
                "findings from a population-based study", "results from a population-based study"
            ],
            
            "randomized_controlled_trial": [
                ": a randomized controlled trial", ": randomized controlled trial", 
                "- randomized controlled trial", ": a randomised controlled trial",
                ": randomised controlled trial", "- randomised controlled trial",
                ": a randomized clinical trial", ": randomized clinical trial",
                "- randomized clinical trial", ": a randomised clinical trial", 
                ": randomised clinical trial", "- randomised clinical trial",
                "a randomized, double-blind,", "a randomised, double-blind,",
                "a randomized, placebo-controlled,", "a randomised, placebo-controlled,",
                "a randomized, double-blind, placebo-controlled,", 
                "a randomised, double-blind, placebo-controlled,",
                
                ": a multicenter randomized controlled trial", ": multicenter randomized controlled trial",
                "- multicenter randomized controlled trial", ": a multicentre randomised controlled trial",
                
                ": a randomized double-blind", ": randomized double-blind", "- randomized double-blind",
                ": a randomised double-blind", ": randomised double-blind", "- randomised double-blind",
                ": a randomized single-blind", ": randomized single-blind", "- randomized single-blind",
                ": a randomised single-blind", ": randomised single-blind", "- randomised single-blind",
                ": a randomized triple-blind", ": randomized triple-blind", "- randomized triple-blind",
                
                ": a randomized placebo-controlled trial", ": randomized placebo-controlled trial",
                "- randomized placebo-controlled trial", ": a randomised placebo-controlled trial",
                ": a randomized active-controlled trial", ": randomized active-controlled trial",
                
                ": a randomized trial", ": randomized trial", "- randomized trial",
                ": a randomised trial", ": randomised trial", "- randomised trial",
                
                "randomized controlled trial of", "randomised controlled trial of",
                "randomized clinical trial of", "randomised clinical trial of", 
                "randomized trial of", "randomised trial of",
                
                "findings from a randomized", "results from a randomized",
                "results of a randomized",
                
                "parallel-group randomized trial", "crossover randomized trial",
                "cluster-randomized trial", "factorial randomized trial",
                "adaptive randomized trial", "pragmatic randomized trial",
                
                "randomized trial in patients with", "randomized controlled trial in",
                
                "randomized trial of", "randomized controlled trial evaluating",
                
                "was randomized to", "were randomly assigned",
                "randomly allocated to", "randomization was performed",
                
                "versus placebo in a randomized", "compared with placebo in a randomized",
                
                "long-term follow-up of a randomized", "extended follow-up of a randomized"
            ],
            
            "non_randomized_trial": [
                ": a non-randomized trial", ": non-randomized trial", "- non-randomized trial",
                ": a non-randomised trial", ": non-randomised trial", "- non-randomised trial",
                ": a non-randomized controlled trial", ": non-randomized controlled trial",
                "- non-randomized controlled trial", ": a non-randomised controlled trial",
                ": non-randomised controlled trial", "- non-randomised controlled trial",
                "non-randomized trial of", "non-randomised trial of",
                "findings from a non-randomized", "results from a non-randomized",
                "results of a non-randomized"
            ],
            
            "quasi_experimental_study": [
                ": a quasi-experimental study", ": quasi-experimental study", "- quasi-experimental study",
                ": a quasi experimental study", ": quasi experimental study", "- quasi experimental study", 
                ": a quasi-experimental design", ": quasi-experimental design", "- quasi-experimental design",
                "quasi-experimental study of", "quasi experimental study of", 
                "findings from a quasi-experimental", "results from a quasi-experimental",
                "results of a quasi-experimental"
            ],
            
            "pragmatic_trial": [
                ": a pragmatic trial", ": pragmatic trial", "- pragmatic trial",
                ": a pragmatic clinical trial", ": pragmatic clinical trial", "- pragmatic clinical trial",
                "pragmatic trial of", "pragmatic clinical trial of",
                "findings from a pragmatic trial", "results from a pragmatic trial",
                "results of a pragmatic trial"
            ],
            
            "pilot_study": [
                ": a pilot study", ": pilot study", "- pilot study",
                ": a pilot trial", ": pilot trial", "- pilot trial",
                ": a pilot randomized", ": pilot randomized", "- pilot randomized",
                ": a pilot randomised", ": pilot randomised", "- pilot randomised",
                "pilot study of", "pilot trial of", "pilot study on",
                "findings from a pilot study", "results from a pilot study",
                "results of a pilot study"
            ],
            
            "feasibility_study": [
                ": a feasibility study", ": feasibility study", "- feasibility study",
                ": a feasibility trial", ": feasibility trial", "- feasibility trial",
                "feasibility study of", "feasibility trial of", "feasibility study on",
                "findings from a feasibility study", "results from a feasibility study",
                "results of a feasibility study"
            ],
            
            "clinical_trial": [
                ": a clinical trial", ": clinical trial", "- clinical trial",
                ": a multicenter clinical trial", ": multicenter clinical trial", "- multicenter clinical trial", 
                ": an open-label clinical trial", ": open-label clinical trial", "- open-label clinical trial",
                ": a phase i clinical trial", ": phase i clinical trial", "- phase i clinical trial",
                ": a phase ii clinical trial", ": phase ii clinical trial", "- phase ii clinical trial",
                ": a phase iii clinical trial", ": phase iii clinical trial", "- phase iii clinical trial",
                ": a phase iv clinical trial", ": phase iv clinical trial", "- phase iv clinical trial",
                "clinical trial of", "clinical trial on", "findings from a clinical trial",
                "results from a clinical trial", "results of a clinical trial"
            ],
        
            "interview_study": [
                ": a qualitative interview study", ": qualitative interview study", "- qualitative interview study",
                ": an interview study", ": interview study", "- interview study",
                ": a semi-structured interview study", ": semi-structured interview study",
                "- semi-structured interview study", "qualitative analysis of interviews",
                "findings from interviews", "qualitative interview analysis"
            ],

            "focus_group_study": [
                ": a focus group study", ": focus group study", "- focus group study",
                ": a qualitative focus group study", ": qualitative focus group study", 
                "- qualitative focus group study", "qualitative analysis of focus groups",
                "findings from focus groups", "focus group analysis"
            ],

            "ethnography": [
                ": an ethnographic study", ": ethnographic study", "- ethnographic study", 
                ": an ethnography", ": ethnography", "- ethnography",
                "ethnographic analysis", "ethnographic findings", "ethnographic observation"
            ],
            
            "phenomenological_study": [
                ": a phenomenological study", ": phenomenological study", "- phenomenological study",
                ": a phenomenology", ": phenomenology", "- phenomenology",
                "phenomenological analysis", "phenomenological investigation",
                "findings from a phenomenological study"
            ],
            
            "grounded_theory_study": [
                ": a grounded theory study", ": grounded theory study", "- grounded theory study",
                ": a grounded theory approach", ": grounded theory approach", "- grounded theory approach",
                "using grounded theory", "grounded theory analysis"
            ],
            
            "case_study_qualitative": [
                ": a qualitative case study", ": qualitative case study", "- qualitative case study",
                "qualitative case study of", "qualitative case study on", 
                "qualitative case study analysis"
            ],
            
            "case_report": [
                ": a case report", ": case report", "- case report",
                ": a case of", ": case of", "- case of",
                "case report of", "case report on", "case presentation",
                ": a rare case of", ": rare case of", "- rare case of",
                ": an unusual case of", ": unusual case of", "- unusual case of"
            ],

            "case_series": [
                ": a case series", ": case series", "- case series",
                ": a series of cases", ": series of cases", "- series of cases",
                "case series of", "case series on", "review of cases",
                "series of patients with", "case series analysis"
            ],
            
            "questionnaire_study": [
                ": a questionnaire study", ": questionnaire study", "- questionnaire study",
                ": a survey study", ": survey study", "- survey study",
                "questionnaire survey", "survey questionnaire", "survey-based study",
                "questionnaire-based study", "findings from a questionnaire survey",
                "results from a questionnaire survey"
            ],

            "delphi_study": [
                ": a delphi study", ": delphi study", "- delphi study",
                ": a delphi survey", ": delphi survey", "- delphi survey",
                ": a modified delphi", ": modified delphi", "- modified delphi",
                "findings from a delphi study", "results from a delphi study"
            ],

            "cost_effectiveness_analysis": [
                ": a cost-effectiveness analysis", ": cost-effectiveness analysis", "- cost-effectiveness analysis",
                ": a cost effectiveness analysis", ": cost effectiveness analysis", "- cost effectiveness analysis",
                "cost-effectiveness of", "cost effectiveness of", "economic evaluation of",
                "findings from a cost-effectiveness analysis", "results from a cost-effectiveness analysis"
            ],

            "cost_utility_analysis": [
                ": a cost-utility analysis", ": cost-utility analysis", "- cost-utility analysis",
                ": a cost utility analysis", ": cost utility analysis", "- cost utility analysis", 
                "cost-utility of", "cost utility of", "cost-utility evaluation",
                "findings from a cost-utility analysis", "results from a cost-utility analysis"
            ],

            "budget_impact_analysis": [
                ": a budget impact analysis", ": budget impact analysis", "- budget impact analysis",
                ": a budget impact model", ": budget impact model", "- budget impact model",
                "budget impact of", "budget impact assessment",
                "findings from a budget impact analysis", "results from a budget impact analysis"
            ],

            "mixed_methods_study": [
                ": a mixed methods study", ": mixed methods study", "- mixed methods study",
                ": a mixed methods approach", ": mixed methods approach", "- mixed methods approach",
                ": a mixed-method study", ": mixed-method study", "- mixed-method study",
                "mixed methods analysis", "mixed methods research", 
                "findings from a mixed methods study", "results from a mixed methods study"
            ],

            "non_formal_study": [
                ": a protocol", ": protocol", "protocol:", "- protocol", "a study protocol", "a research protocol", "protocol of", "protocol for",
                ": an erratum", ": erratum", "erratum:", "- erratum", "erratum for", "erratum of", "correction and erratum", "correction to", "correction:"
                ": a letter", ": letter", "- letter", "letter to the editor", "letter to the editor:", "letter to the editor regarding", "letter to the editor about", "letter commenting on", "letter concerning",
                ": a comment", ": comment", "- comment", "comment on", "comment regarding", "comment about", "commenting on",
                ": a commentary", ": commentary", "- commentary", "commentary on", "commentary regarding", "commentary about", "commentary concerning",
                ": an commentary", ": editorial", "- editorial",
                ": a perspective", ": perspective", "- perspective",
                ": an opinion", ": opinion", "- opinion",
                ": a correspondence", ": correspondence", "- correspondence",
                "editorial on", "editorial and perspective", "editorial regarding", "editorial about",
                "perspective and commentary", "response to comments", "commentary on the article", "correspondence and response",
                "response to the editor", "response to the letter", "response to the commentary",
            ]
        }

        self.title_high_sensitivity_keywords = {
            "randomized_controlled_trial": [
                "rct", "randomized", "randomised", "random", "trial", "controlled trial",
                "clinical trial", "placebo", "double-blind", "single-blind", "blinded",
                "allocation", "assigned", "randomization", "randomisation"
            ],
        }

        self.abstract_high_specificity_keywords = {
            "systematic_review": [
                "we conducted a systematic review", "we performed a systematic review",
                "this systematic review", "in this systematic review",
                "we systematically reviewed", "the aim of this systematic review",
                "the purpose of this systematic review", "we undertook a systematic review",
                "objective of this systematic review", "protocol for this systematic review",
                "methodology of this systematic review"
            ],

            "meta_analysis": [
                "we conducted a meta-analysis", "we performed a meta-analysis",
                "this meta-analysis", "in this meta-analysis", "pooled analysis showed", 
                "we pooled data from", "we pooled the results", "pooled estimate",
                "the aim of this meta-analysis", "the purpose of this meta-analysis",
                "we undertook a meta-analysis", "data were pooled using",
                "data was pooled using", "pooled risk ratio", "pooled odds ratio",
                "pooled relative risk", "pooled mean difference", "random-effects meta-analysis",
                "fixed-effects meta-analysis"
            ],

            "network_meta_analysis": [
                "we conducted a network meta-analysis", "we performed a network meta-analysis",
                "this network meta-analysis", "in this network meta-analysis",
                "bayesian network meta-analysis was performed", 
                "frequentist network meta-analysis was conducted",
                "network of evidence", "network geometry", "network plot",
                "mixed treatment comparison", "multiple treatments meta-analysis",
                "ranking probability", "surface under the cumulative ranking",
                "sucra values", "league table", "consistency assumption",
                "inconsistency was assessed", "node-splitting approach"
            ],

            "narrative_review": [
                "we conducted a narrative review", "we performed a narrative review",
                "this narrative review", "in this narrative review",
                "the aim of this narrative review", "the purpose of this narrative review",
                "objective of this narrative review", "methodology of this narrative review"
            ],

            "scoping_review": [
                "we conducted a scoping review", "we performed a scoping review",
                "this scoping review", "in this scoping review",
                "the aim of this scoping review", "the purpose of this scoping review",
                "objective of this scoping review", "methodology of this scoping review",
                "we followed the joanna briggs institute methodology",
                "we followed the arksey and o'malley framework"
            ],
            
            "cohort_study": [
                "prospective cohort of patients", "retrospective cohort of patients",
                "in this cohort study", "we conducted a cohort study",
                "data from a cohort study", "cohort was followed for",
                "cohort was followed up for", "patients were followed for",
                "subjects were followed for", "participants were followed for",
                "follow-up period", "this prospective cohort study",
                "this retrospective cohort study", "nested cohort study",
                "inception cohort", "dynamic cohort", "fixed cohort"
            ],
            
            "case_control_study": [
                "case-control design", "matched cases and controls",
                "in this case-control study", "we conducted a case-control study",
                "cases were compared with controls", "cases and controls were matched",
                "we matched cases and controls", "odds ratios were calculated",
                "odds ratio was calculated", "conditional logistic regression",
                "this case-control study", "nested case-control study"
            ],
            
            "cross_sectional_study": [
                "cross-sectional design", "in this cross-sectional study",
                "we conducted a cross-sectional study", "cross-sectional analysis of",
                "this cross-sectional study", "cross-sectional survey",
                "one-time assessment", "point prevalence", "single time point"
            ],
            
            "randomized_controlled_trial": [
                "patients were randomly assigned", "participants were randomized to",
                "subjects were randomly allocated", "randomization was performed",
                "randomisation was performed", "double-blind", "triple-blind",
                "allocation concealment", "intention-to-treat analysis",
                "in this randomized controlled trial", "we conducted a randomized controlled trial",
                "this randomized clinical trial", "this randomised controlled trial", 
                "random sequence generation", "blocked randomization",
                "stratified randomization", "cluster randomization"
            ],

            "case_report": [
                "we report a case of", "herein we report a case", 
                "this case report describes", "in this case report",
                "we present a case of", "we describe a case of",
                "we present a patient with", "we describe a patient with",
                "to our knowledge, this is the first reported case of",
                "a rare case of", "an unusual case of", "a unique case of"
            ],
            
            "case_series": [
                "we report a series of cases", "this case series describes",
                "in this case series", "we present a case series",
                "we describe a series of", "we analyzed a series of",
                "consecutive cases of", "consecutive patients with",
                "retrospective analysis of cases", "retrospective review of cases"
            ],
            
            "qualitative_study": [
                "qualitative methodology", "qualitative approach",
                "thematic analysis", "content analysis", "framework analysis",
                "qualitative interviews", "focus group discussions", 
                "we conducted a qualitative study", "this qualitative study",
                "in this qualitative study", "qualitative data were analyzed",
                "qualitative data was analyzed", "qualitative data collection",
                "data saturation", "purposive sampling", "theoretical sampling"
            ],

            "mixed_methods_study": [
                "mixed methods approach", "mixed methodology",
                "both qualitative and quantitative methods", "both qualitative and quantitative data",
                "we employed a mixed methods design", "sequential explanatory design",
                "sequential exploratory design", "convergent parallel design",
                "we conducted a mixed methods study", "this mixed methods study"
            ],

            "non_formal_study": [
                "we conducted a protocol", "this protocol", "in this protocol",
                "we report an erratum", "this erratum", "in this erratum",
                "we write a letter", "this letter", "in this letter",
                "we provide a comment", "this comment", "in this comment",
                "we offer a commentary", "this commentary", "in this commentary",
                "we publish an editorial", "this editorial", "in this editorial",
                "we share a perspective", "this perspective", "in this perspective",
                "we express an opinion", "this opinion", "in this opinion",
                "we send a correspondence", "this correspondence", "in this correspondence"
            ]
        }

        self.abstract_high_sensitivity_keywords = {
            "randomized_controlled_trial": [
                "patients were randomly assigned", "participants were randomized to",
                "subjects were randomly allocated", "randomization was performed",
                "randomisation was performed", "double-blind", "triple-blind",
                "allocation concealment", "intention-to-treat analysis",
                "in this randomized controlled trial", "we conducted a randomized controlled trial",
                "this randomized clinical trial", "this randomised controlled trial", 
                "random sequence generation", "blocked randomization",
                "stratified randomization", "cluster randomization",
                "randomly assigned", "randomly allocated", "random allocation",
                "placebo-controlled", "control group", "treatment group",
                "intervention group", "experimental group"
            ],
        }
        
    def check_study_design(self, title, abstract, excluded_designs, included_designs=None):
        """
        Check if the study design should be excluded
        
        Args:
            title: Title of the article
            abstract: Abstract of the article
            excluded_designs: List of study designs to exclude
            included_designs: List of study designs to include (default is RCT)
            
        Returns:
            tuple: (should_exclude, design_type, matched_keyword, details)
        """
        if included_designs is None:
            included_designs = ["randomized_controlled_trial"]
        
        title_lower = title.lower()
        abstract_lower = abstract.lower()
        
        # Check title and abstract separately
        title_should_exclude, title_details = self._check_section(
            title_lower, excluded_designs, included_designs, "title"
        )
        
        abstract_should_exclude, abstract_details = self._check_section(
            abstract_lower, excluded_designs, included_designs, "abstract"  
        )
        
        # Check if any section matched a high-sensitivity inclusion keyword
        has_inclusion_match = (
            title_details.get('matched_included_keyword') is not None or 
            abstract_details.get('matched_included_keyword') is not None
        )
        
        # New logic:
        # 1. Exclude if either title or abstract meets exclusion criteria and there's no inclusion match
        # 2. Do not exclude if there's an inclusion match (higher priority)
        
        if has_inclusion_match:
            # Inclusion match found, do not exclude
            return False, None, None, {
                'title': title_details,
                'abstract': abstract_details,
                'reason': 'Found inclusion match, overrides exclusion'
            }
        
        # If no inclusion match, check for exclusion matches
        if title_should_exclude:
            design_type     = title_details['design_type']
            matched_keyword = title_details['matched_excluded_keyword']
            print(f"Prefilter: EXCLUDE – {design_type} (matched: {matched_keyword})")
            return True, design_type, matched_keyword, {
                'title':     title_details,
                'abstract':  abstract_details,
                'reason':   'Title meets exclusion criteria and no inclusion match found'
            }
        if abstract_should_exclude:
            design_type     = abstract_details['design_type']
            matched_keyword = abstract_details['matched_excluded_keyword']
            print(f"Prefilter: EXCLUDE – {design_type} (matched: {matched_keyword})")
            return True, design_type, matched_keyword, {
                'title':     title_details,
                'abstract':  abstract_details,
                'reason':   'Abstract meets exclusion criteria and no inclusion match found'
            }
        
        # Neither meets exclusion criteria
        print("Prefilter: PASSED")
        return False, None, None, {
            'title':     title_details,
            'abstract':  abstract_details,
            'reason':   'No exclusion criteria met'
        }

    def _check_section(self, text, excluded_designs, included_designs, section_type):
        """
        Check if a single section (title or abstract) should be excluded
        
        Args:
            text: Text to check (lowercase)
            excluded_designs: List of study designs to exclude
            included_designs: List of study designs to include
            section_type: "title" or "abstract"
            
        Returns:
            tuple: (should_exclude, details_dict)
        """
        details = {
            'section': section_type,
            'matched_excluded_keyword': None,
            'matched_included_keyword': None,
            'design_type': None,
            'should_exclude': False
        }
        
        # Select the corresponding keyword library
        if section_type == "title":
            excluded_keywords_dict = self.title_high_specificity_keywords
            included_keywords_dict = self.title_high_sensitivity_keywords
        else:  # abstract
            excluded_keywords_dict = self.abstract_high_specificity_keywords
            included_keywords_dict = self.abstract_high_sensitivity_keywords

        # Check for matches in the exclusion keyword library
        excluded_match = False
        for design_type in excluded_designs:
            if design_type in excluded_keywords_dict:
                for keyword in excluded_keywords_dict[design_type]:
                    if keyword.lower() in text:
                        details['matched_excluded_keyword'] = keyword
                        details['design_type'] = design_type
                        excluded_match = True
                        break
                if excluded_match:
                    break
        
        # If no exclusion keywords matched, this section should not be excluded
        if not excluded_match:
            return False, details
        
        # Check for matches in the inclusion keyword library
        included_match = False
        for design_type in included_designs:
            if design_type in included_keywords_dict:
                for keyword in included_keywords_dict[design_type]:
                    if keyword.lower() in text:
                        details['matched_included_keyword'] = keyword
                        included_match = True
                        break
                if included_match:
                    break
        
        # If exclusion keywords matched but inclusion keywords did not, exclude this section
        if excluded_match and not included_match:
            details['should_exclude'] = True
            return True, details
        
        return False, details  