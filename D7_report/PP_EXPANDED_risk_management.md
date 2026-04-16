# PP EXPANDED -- Risk Management

> Extracted from `D7_report/professional_practice/risk_management/RISK_MANAGEMENT_COMPLETE.md`
> Every actionable concept with D7 application mapping.

---

## Concepts

```
{
  id: RM-01,
  pri: HIGH,
  name: "ISO 31000 Definition of Risk",
  src: "ISO 31000:2018; Graham Video 2 slide s04",
  sections: "B.2",
  how: "Open the risk section with this formal definition. Frame every project risk (GPS loss, weather, detection failure) as 'uncertainty affecting our objective of autonomous casualty location.' Shows Apollo knows the standard, not just colloquial usage.",
  quote: "Risk is 'the effect of uncertainty on objectives.' -- ISO 31000:2018",
  ref: "iso31000:2018"
}
```

```
{
  id: RM-02,
  pri: HIGH,
  name: "Risk as Choice (Risacare Etymology)",
  src: "Graham Video 2; Bernstein 1996",
  sections: "B.2",
  how: "Use in the introduction to reframe risk as deliberate engineering choice, not passive fate. 'We chose to fly at 35m (accepting lower detection confidence) rather than 20m (accepting 3x longer mission time). Risk is a choice we made deliberately.' Elevates tone from descriptive to analytical.",
  quote: "The word 'risk' derives from the early Italian risicare, meaning 'to dare.'",
  ref: "bernstein1996gods"
}
```

```
{
  id: RM-03,
  pri: HIGH,
  name: "Six Risk Types (Safety, Schedule, Financial, Performance, Quality, Environmental)",
  src: "Graham Video 2 slides s03-s04",
  sections: "B.3",
  how: "Categorise each entry in the SAR drone risk register under these types. Show at least 3 types in the D7 discussion: Safety (drone crash / SSSI incursion), Schedule (3 cancelled flight days), Performance (AI detection rate at altitude). Demonstrates breadth of risk thinking beyond just 'safety.'",
  quote: "N/A -- classification from lecture slides",
  ref: "graham2023risk"
}
```

```
{
  id: RM-04,
  pri: HIGH,
  name: "Hazard vs Risk Distinction",
  src: "Graham Video 2 slide s05; ISO 31000",
  sections: "B.4",
  how: "Be precise in language: 'The hazard is the spinning propeller. The risk is the likelihood of contact multiplied by the consequence of laceration.' Examiners notice when students conflate hazard and risk. Use the ISO definitions verbatim.",
  quote: "Hazard: 'Something that has the potential to do harm.' Risk combines hazard with likelihood and consequence.",
  ref: "iso31000:2018"
}
```

```
{
  id: RM-05,
  pri: CRITICAL,
  name: "Risk Number = Likelihood x Consequence",
  src: "Graham Video 2 slide s08-s10",
  sections: "B.8, B.11",
  how: "Score every risk in the SAR drone register with f and c values. Show the multiplication. Map to the criticality matrix (RM-14). The weather-cancellation risk (f=4, c=3, fxc=12 INTOLERABLE) is the strongest example because it actually materialised. Show pre- and post-mitigation scores where possible.",
  quote: "The resulting number guides you as to what to do.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-06,
  pri: HIGH,
  name: "Mitigations: Reduce Likelihood, Reduce Consequence, or Both",
  src: "Graham Video 2 slides s05-s06 (climbing example)",
  sections: "B.5",
  how: "Map each SAR drone mitigation to the L/C framework explicitly. Geofence = reduces BOTH (prevents entry AND auto-returns). RC kill switch = reduces CONSEQUENCE only (hazard still occurs but pilot regains control). Progressive test ladder = reduces LIKELIHOOD (catches bugs before flight). This is the analytical move that gets L4.",
  quote: "Different mitigations can improve the likelihood, consequence, or both.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-07,
  pri: CRITICAL,
  name: "Risk Compensation (Helmet Makes You Careless)",
  src: "Graham Video 2 slide s06; electrician example",
  sections: "B.6",
  how: "This is the highest-value concept for D7 because it shows CRITICAL SELF-REFLECTION. Apply it twice: (1) NCNN giving 4.5x faster inference could tempt higher flight speed, reducing detection window -- the speed improvement makes us feel safer and therefore less cautious. (2) Successful simulation (7.7/10) created overconfidence, reducing urgency of hardware testing, which was then blocked by weather. Both are honest self-critique = L4 Hatton.",
  quote: "The climber might think they are safer because they have a helmet and be less careful about holding on.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-08,
  pri: MEDIUM,
  name: "Electricians Overconfident in Circuit Breakers",
  src: "Graham Video 2 (verbatim lecture quote)",
  sections: "B.6",
  how: "Use as a parallel analogy when discussing risk compensation in the project. 'Just as Graham observed electricians becoming careless because they trust modern circuit breakers, our team's trust in the software geofence could reduce vigilance about GPS accuracy -- the very input the geofence depends on.'",
  quote: "Electricians seem increasingly careless when operating on live circuits... overconfident in the performance of modern circuit breakers.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-09,
  pri: HIGH,
  name: "HSE 5-Step Risk Assessment Cycle",
  src: "Graham Video 2 slide s07; HSE guidance",
  sections: "B.7",
  how: "Map each step to a concrete project action: (1) Identify -- listed 12 hazards in risk register. (2) Assess -- scored f x c using 5x5 matrix. (3) Control -- implemented geofence, kill switch, test ladder. (4) Record -- risk register in project documentation + flight day checklist. (5) Review -- re-scored 'AI fails to detect' from f=2 to f=4 after corrupt calibration_data.npz incident. The CYCLIC nature is key -- show you went around the loop more than once.",
  quote: "The process is cyclic -- risk assessments should be reviewed on a regular basis.",
  ref: "hse5steps"
}
```

```
{
  id: RM-10,
  pri: HIGH,
  name: "Risk Assessment Pro Forma (9 Columns)",
  src: "Graham Video 2 slides s08-s10",
  sections: "B.8",
  how: "Use exactly this 9-column format for the SAR drone risk register in D7. Columns: Date/Initials, Type, Hazard, Consequence, Frequency, Consequence Score, Risk Number, Mitigation, Residual Risk. Having a properly formatted table with all 9 columns shows direct application of the taught framework.",
  quote: "N/A -- pro forma structure from lecture slides",
  ref: "graham2023risk"
}
```

```
{
  id: RM-11,
  pri: MEDIUM,
  name: "Frequency Scoring (1-5 Logarithmic Scale)",
  src: "Graham Video 2 slide s09",
  sections: "B.9",
  how: "Define project-specific frequency scale. Example: 1 = once in 1000 flights, 2 = once in 100 flights, 3 = once in 50 flights, 4 = once in 10 flights, 5 = every flight. Note the logarithmic nature -- the jump from 4 to 5 is not linear. Apply to: GPS loss (f=2), weather cancellation (f=4), hot-tyre-equivalent detection failure (f=3).",
  quote: "The scales are rarely linear and more often logarithmic.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-12,
  pri: MEDIUM,
  name: "Consequence Scoring (Network Rail Examples)",
  src: "Graham Video 2 slide s11; Network Rail pro forma",
  sections: "B.10",
  how: "Adapt Network Rail's 5-level consequence scale to the SAR drone context. 1=Minor (scratch on drone), 2=Minor injury (bruise from prop), 3=Moderate (drone destroyed, major injury), 4=Major (multiple injuries, SSSI damage, legal action), 5=Catastrophic (fatality). Citing Network Rail as precedent shows industry awareness.",
  quote: "Network Rail consequence scale ranges from 'Minor safety event' (1) to 'Catastrophic Safety event with potential of over 10 fatalities' (5).",
  ref: "networkrail_ra"
}
```

```
{
  id: RM-13,
  pri: MEDIUM,
  name: "Pre/Post Mitigation Scoring (Residual Risk)",
  src: "Graham Video 2 slides s08-s10",
  sections: "B.8, B.13",
  how: "For at least 2 risks, show BEFORE and AFTER mitigation scores. Example: 'SSSI incursion: pre-mitigation f=3, c=4, fxc=12 (Intolerable). Post-mitigation (geofence + 10m buffer + RC override): f=1, c=4, fxc=4 (Negligible).' This demonstrates the value of mitigations quantitatively and shows residual risk awareness.",
  quote: "The residual risk is the risk that remains even after I've deployed my mitigations. Most mitigations don't remove the risk altogether.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-14,
  pri: HIGH,
  name: "5x5 Criticality Matrix (Negligible / Tolerable / Intolerable)",
  src: "Graham Video 2 slide s12",
  sections: "B.12",
  how: "Include the 5x5 matrix in D7 (or reference it). Plot project risks on it. Key insight: 1-5 = Negligible (no action), 6-10 = Tolerable (action plan needed), 11-25 = Intolerable (HALT activity). The weather risk at fxc=12 fell into Intolerable -- which is exactly what happened (flights were halted). This is powerful evidence of the framework working.",
  quote: "11-25: Intolerable. Activity must halt. Resumption requires approval from the safety board.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-15,
  pri: CRITICAL,
  name: "ALARP (As Low As Reasonably Practicable)",
  src: "Graham Video 1 slide s14; HSAWA Section 2",
  sections: "A.8",
  how: "Apply ALARP to at least one concrete decision with NUMBERS. Best example: 'Reducing search altitude from 35m to 20m would increase detection confidence by ~15% but require 3.1x more passes, extending mission from 8 to 25 minutes. We judged this not reasonably practicable.' Also: using TFLite (206ms, proven) instead of waiting for NCNN (72ms, untested on Pi). ALARP with quantitative reasoning = L4.",
  quote: "In most cases there are no hard and fast rules about what is reasonably practical and often it is reliant on the experience of company safety experts.",
  ref: "hsawa1974"
}
```

```
{
  id: RM-16,
  pri: LOW,
  name: "VPF (Value of Prevented Fatality)",
  src: "Graham Video 1 slide s14; DfT 2016",
  sections: "A.8",
  how: "Mention briefly as context for how industry quantifies ALARP decisions. '1.83M GBP per fatality (DfT, 2016) provides a framework for cost-benefit analysis of safety investments. While our university project operates at a different scale, the principle of comparing mitigation cost against risk reduction benefit applies equally.' Shows awareness of professional-scale risk economics.",
  quote: "Would you spend 5,000,000 to save 20 lives or 5,000,000 to save 50 lives? You instinctively perform a benefit calculation.",
  ref: "dft_vpf2016"
}
```

```
{
  id: RM-17,
  pri: HIGH,
  name: "Three Pillars: Moral, Economic, Legal",
  src: "Graham Video 1 slides s12-s13",
  sections: "A.6",
  how: "Show ALL THREE pillars influenced a single decision. Best example: RC override guard. Moral = pilot must always protect bystanders. Economic = crash destroys ~2000 GBP equipment. Legal = drone operator bears personal liability under ANO 2016. Connecting all three to one concrete decision = L4 synthesis.",
  quote: "You have a moral obligation to work safely and ensure the safety of others around you. This obligation is above all others.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-18,
  pri: HIGH,
  name: "'Reasonably Practicable' Concept",
  src: "Graham Video 1; HSAWA 1974 Section 2",
  sections: "A.4, A.8",
  how: "Show you understand this is a LEGAL STANDARD, not just common sense. It requires a cost-benefit analysis: the cost of mitigation must be weighed against the degree of risk. 'Reasonably practicable' appears 7+ times in HSAWA Section 2. Apply: 'Adding a secondary GPS receiver would further reduce navigation risk, but at ~500 GBP cost and added weight/complexity, this was not reasonably practicable for a university prototype.'",
  quote: "Duty upon employers to ensure, as far as is reasonably practicable, the health, safety and welfare of employees.",
  ref: "hsawa1974"
}
```

```
{
  id: RM-19,
  pri: MEDIUM,
  name: "Duty of Care (Priestley v Fowler 1835)",
  src: "Graham Video 1 slide s06",
  sections: "A.2.2",
  how: "Brief historical mention to show depth of legal knowledge. 'The concept of employer duty of care dates to Priestley v Fowler (1835), where a servant injured by an overloaded wagon established that employers owe employees a duty of care. In our project, this translates to the team lead's responsibility to ensure flight day procedures protect all team members.'",
  quote: "Landmark: established that employers owe employees a duty of care.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-20,
  pri: HIGH,
  name: "Flixborough Disaster (1974) -- Catalyst for HSAWA",
  src: "Graham Video 1 slides s07-s08",
  sections: "A.3",
  how: "Use as the historical anchor when introducing HSAWA. '28 deaths from a temporary piping fix that failed, releasing 20-40 tonnes of cyclohexane. Estimated 500 deaths had it occurred on a weekday. This single event accelerated HSAWA implementation.' Then pivot: 'Our project's progressive test ladder -- bench before flight, passive before autonomous -- embodies the same principle: never skip safety steps to save time.'",
  quote: "Flixborough accelerated the implementation of the Health and Safety at Work Act.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-21,
  pri: MEDIUM,
  name: "Corporate Manslaughter Act 2007",
  src: "Graham Video 1 slide s13",
  sections: "A.7",
  how: "Mention as evidence of evolving legal landscape. Cite Cotswold Geotechnic (2008, 385K fine for trench collapse killing a geologist). 'The Act enables prosecution of organisations, not just individuals. While our university project is not a corporate entity, the principle that systemic failures -- not just individual errors -- cause harm is directly relevant to our software architecture decisions.'",
  quote: "Enables prosecution of organisations as well as individuals.",
  ref: "cma2007"
}
```

```
{
  id: RM-22,
  pri: CRITICAL,
  name: "'Working Alone on Risk Assessment Is Suboptimal'",
  src: "Graham Video 2 slide s10",
  sections: "B.8",
  how: "Use to justify team-based risk assessment AND to acknowledge a weakness. 'Graham emphasises that a diversity of views is needed to capture more eventualities (2023). Our risk register was primarily authored by one team member (DC), which risks blind spots. However, the progressive test ladder served as an implicit peer review -- each test step exposed the system to a different team member's scrutiny.'",
  quote: "Working alone on a risk assessment is suboptimal as a diversity of views are needed to capture more of the eventualities.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-23,
  pri: MEDIUM,
  name: "'No One Has to Be Harmed for an Offence'",
  src: "Graham Video 1 slide s09; HSAWA",
  sections: "A.4",
  how: "Use to justify why the geofence matters even though no actual SSSI incursion occurred. 'Under HSAWA, creating a risk of harm is itself an offence -- actual harm need not occur. Our geofence implementation therefore serves a legal function: it demonstrates that we took reasonably practicable steps to prevent NFZ incursion, regardless of whether incursion ever happened.'",
  quote: "No one has to be harmed for an offence to be committed under the Act -- there only has to be a risk of harm.",
  ref: "hsawa1974"
}
```

```
{
  id: RM-24,
  pri: MEDIUM,
  name: "Risk Assessment Is Continuous and Unconscious",
  src: "Graham Video 2 opening remarks",
  sections: "B.2",
  how: "Use as a bridge from theory to practice. 'Risk assessing is something we do continuously but unconsciously every day -- crossing a road, choosing a route. The value of formalised risk management (Graham, 2023) is making this implicit process explicit, auditable, and transferable. Our risk register makes the team's collective risk judgments visible to any successor.'",
  quote: "Risk assessing is something you do continuously but unconsciously every day.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-25,
  pri: LOW,
  name: "Secondary Legislation / Regulations",
  src: "Graham Video 1 slide s10",
  sections: "A.5",
  how: "Brief mention to show awareness of the legislative hierarchy. 'HSAWA provides the overarching framework; specific regulations (RIDDOR 2013, COSHH 2002, Manual Handling 1992) address particular hazards. For drone operations, the Air Navigation Order 2016 and CAA CAP 722 provide equivalent domain-specific regulation.' Shows you understand primary vs secondary legislation.",
  quote: "N/A -- list of 12 regulations from slide s10",
  ref: "graham2023safety"
}
```

```
{
  id: RM-26,
  pri: LOW,
  name: "HSE Inspectors Have Greater Powers Than Police",
  src: "Graham Video 1 slide s10",
  sections: "A.5",
  how: "Brief mention for flavour/depth. 'HSE inspectors can access any workplace at any time without a warrant -- powers exceeding those of the police. This reflects the seriousness with which the state treats workplace safety.'",
  quote: "HSE inspectors have greater powers than the police -- they have the right to access any place of work at any time, without a warrant.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-27,
  pri: MEDIUM,
  name: "HSAWA Six Employer Duties",
  src: "Graham Video 1 slide s11 (Section 2 extract)",
  sections: "A.4",
  how: "Map at least 3 of the 6 duties to the project. (1) 'Provide plant and systems that are safe' = our progressive test ladder validates the system before flight. (3) 'Deliver adequate training' = flight day checklist + briefing before each test step. (5) 'Written H&S Policy' = documented risk register + flight day checklist + pre-flight checks. Shows the university project mirrors professional obligations.",
  quote: "N/A -- 6 duties from HSAWA Section 2",
  ref: "hsawa1974"
}
```

```
{
  id: RM-28,
  pri: MEDIUM,
  name: "Mental Health as Employer Duty",
  src: "Graham Video 1 slide s11 (note after duties)",
  sections: "A.4",
  how: "Brief but impactful mention. 'Graham notes that employer duty of care extends to mental health, not just physical. In our project, the pressure of three cancelled flight days and a fixed deadline created significant stress. The mitigation -- having a simulation-first fallback plan -- reduced both schedule risk and team anxiety.'",
  quote: "Employers also have a duty of care for employees' mental health, not just physical health.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-29,
  pri: MEDIUM,
  name: "F1 Pit-Stop Risk Assessment (Worked Example)",
  src: "Graham Excel Quiz",
  sections: "C.1, C.2",
  how: "Reference as an example of domain-specific frequency/consequence scales. 'The F1 pit-stop assessment (Graham, 2023) uses event-specific scales (1/1000 to >1/10 pit stops) rather than generic ones. Similarly, our SAR drone frequency scale should be flight-specific: 1 = once per 1000 flights, 5 = every flight.' Also: the quiz shows consequence scales can be multi-dimensional (safety + performance), which we mirror with safety + schedule risks.",
  quote: "N/A -- worked example from quiz spreadsheet",
  ref: "graham2023risk"
}
```

```
{
  id: RM-30,
  pri: LOW,
  name: "FMEA Variants (DFMEA, PFMEA, IFMEA, FMECA)",
  src: "Graham Video 2 slide s08",
  sections: "B.8",
  how: "Brief mention to show awareness of alternative risk tools beyond the basic pro forma. 'While we used a standard risk assessment pro forma, more complex systems would benefit from DFMEA (design) or FMECA (criticality analysis). A DFMEA of the GPS-to-geofence dependency chain would have formally captured the cascading failure mode we discovered during field testing.'",
  quote: "N/A -- types listed on slide",
  ref: "graham2023risk"
}
```

```
{
  id: RM-31,
  pri: HIGH,
  name: "Mitigations May Cause Unwanted Additional Risks",
  src: "Graham Video 2 slide s10",
  sections: "B.8",
  how: "Apply to a concrete example. 'The emergency RTL geofence is a mitigation for SSSI incursion, but it introduces a secondary risk: if triggered near the ground, the sudden mode change could cause an uncontrolled climb-and-return while the pilot expects manual control. We mitigated this secondary risk with the RC override guard -- but this chain of mitigation-upon-mitigation illustrates Graham's warning.'",
  quote: "Mitigations may cause unwanted additional risks, so be careful as this is where the unexpected can happen.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-32,
  pri: MEDIUM,
  name: "Non-Experts Add Value to Risk Assessment",
  src: "Graham Video 2 slide s10",
  sections: "B.8",
  how: "Use to discuss team composition for risk review. 'Graham notes that non-experts often ask great questions and notice things specialists miss. During our bench testing, a team member without software background asked why the drone would obey commands if GPS was lost -- prompting us to add the GPS-fix pre-condition to the resume-from-override logic.'",
  quote: "Non-experts often ask great questions... they might notice things that you hadn't noticed before.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-33,
  pri: LOW,
  name: "Improvement Since 1974 (651 to 150 Fatalities)",
  src: "Graham Video 1 slide s15",
  sections: "A.9",
  how: "Brief context to show the framework works. '77% reduction in workplace fatalities since HSAWA (651 to ~150/year), despite 11 million population increase. But 150 is still not zero -- Graham asks 'Is that good enough? No.' This continuous-improvement mindset directly informs our iterative risk review cycle.'",
  quote: "Is that good enough? Well, no, not really. 150 fatalities is still a very high number.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-34,
  pri: MEDIUM,
  name: "'Don't Walk By' -- Report Hazards",
  src: "Graham Video 1 slide s16",
  sections: "A.10",
  how: "Apply to team culture on flight day. 'Graham's instruction to never walk by a hazard was operationalised in our flight day protocol: any team member could call a halt at any time, and the pre-flight checklist required sign-off from all present members before proceeding to each test step.'",
  quote: "If you see something you don't like, please don't walk by, report it. You might just save their life.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-35,
  pri: MEDIUM,
  name: "'Professional Approach Starts Now'",
  src: "Graham Video 1 slide s16",
  sections: "A.10",
  how: "Use as a closing or bridging statement. 'Graham's instruction that professional safety practice starts at university, not at first employment, motivated our decision to implement full risk management tooling -- geofence, kill switch, progressive testing -- on a student project where none was strictly required. This is practice for the professional standard we intend to maintain.'",
  quote: "Your professional approach to working safely starts now.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-36,
  pri: HIGH,
  name: "Iterative Risk Re-Assessment (Review the Controls)",
  src: "Graham Video 2 slide s07 (Step 5); D.15.6",
  sections: "B.7, D.15",
  how: "This is the strongest L4 move available. Show that you went around the HSE 5-step cycle MORE THAN ONCE. 'After field testing revealed corrupt calibration_data.npz causing detection failure, we re-scored the AI-fails-to-detect hazard from f=2 to f=4 and added a pre-flight model validation step. This iterative re-assessment -- not just initial scoring -- is what Graham identifies as the hallmark of mature risk management.'",
  quote: "This assessment requires an update by [date] -- ensures documents are kept current.",
  ref: "hse5steps"
}
```

```
{
  id: RM-37,
  pri: LOW,
  name: "Peter Bernstein / Against the Gods",
  src: "Graham Video 2 opening; Bernstein 1996",
  sections: "B.2",
  how: "Optional scholarly reference for depth. 'Bernstein (1996) argues that humanity's ability to manage risk -- rather than defer to fate -- is what distinguishes modern civilisation. Pascal and Fermat's probability theory, developed for gambling, became the foundation of actuarial science and engineering risk management.'",
  quote: "Humanity's changed approach to risk is what separates modern from ancient times.",
  ref: "bernstein1996gods"
}
```

```
{
  id: RM-38,
  pri: MEDIUM,
  name: "Risk Management as Art, Not Just Science",
  src: "Graham Video 2 opening",
  sections: "B.2",
  how: "Use to acknowledge that risk scoring involves judgment, not just calculation. 'Graham describes risk management as an art -- the frequency and consequence scores are informed by experience, not measured precisely. Our team's limited flight experience is itself a risk factor: we lack the operational intuition that professional drone operators bring to risk assessment.'",
  quote: "The art of risk management, for it is an art, is the most important activity of any senior manager in a technical field.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-39,
  pri: LOW,
  name: "Risk Management Unlocks Opportunity",
  src: "Graham Video 2 closing",
  sections: "B.14 (closing remarks)",
  how: "Use as a closing statement linking risk management to professional development. 'Graham notes that demonstrated risk management skill unlocks access to the most exciting projects -- those involving high levels of risk. Our SAR drone project, with its autonomous flight, AI decision-making, and safety-critical requirements, exemplifies this: the project's ambition was only possible because of the risk management framework we built around it.'",
  quote: "Showing that you are skilled in risk management can also help unlock greater investment or personal opportunity, as the most exciting projects often involve high levels of risk.",
  ref: "graham2023risk"
}
```

```
{
  id: RM-40,
  pri: MEDIUM,
  name: "Strong Safety Culture Drives Continuous Improvement",
  src: "Graham Video 1 slide s15",
  sections: "A.9",
  how: "Apply to the progressive test ladder philosophy. 'Graham argues that the best businesses drive continuous safety improvement even when the record is already good. Our progressive test ladder embodies this: even after successful simulation, we did not skip to autonomous flight -- each intermediate step (bench, passive, waypoint) was a deliberate safety gate.'",
  quote: "The best businesses will be those that have a strong health and safety culture at their core and a management ethos that drives for continuous improvements in safety.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-41,
  pri: LOW,
  name: "White Phosphorus / Phossy Jaw (Industrial Hazard Example)",
  src: "Graham Video 1 slide s04",
  sections: "A.2.3",
  how: "Optional historical colour. 'Industrial hazards like phossy jaw (jawbone necrosis from white phosphorus in matchmaking, fatal in ~20% of cases, not banned in Britain until 1910) illustrate the human cost of inadequate regulation. HSAWA 1974 was the legislative response to decades of such harm.'",
  quote: "N/A -- historical example from lecture",
  ref: "graham2023safety"
}
```

```
{
  id: RM-42,
  pri: HIGH,
  name: "Cascading/Compounding Risk (Beyond Simple f x c)",
  src: "D.17 Hatton L4 Moves",
  sections: "B.11, D.17",
  how: "CRITIQUE the framework to hit L4. 'The standard criticality matrix assumes independent risks, but in our system GPS-loss (f=2, c=5) cascades into both geofence failure and navigation failure, compounding the effective risk beyond the simple f x c product. A fault-tree analysis would better capture these dependencies.' This is the meta-move: showing you understand the limits of the tool you are using.",
  quote: "N/A -- original critical analysis",
  ref: "graham2023risk"
}
```

```
{
  id: RM-43,
  pri: MEDIUM,
  name: "Supplier Safety Records / Economic Pillar",
  src: "Graham Video 1 slide s12",
  sections: "A.6",
  how: "Brief mention under the economic pillar. 'Good businesses refuse to work with suppliers that have weak safety records (Graham, 2023). Supplier awards involve review of H&S procedures and improvement plans. In the drone industry, this translates to customer trust in autonomous systems -- a history of safe operations is a competitive advantage.'",
  quote: "Any good business will refuse to work with a supplier or partner that has a weak safety record.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-44,
  pri: LOW,
  name: "Factory Act 1802 -- No Enforcement Powers",
  src: "Graham Video 1 slide s05",
  sections: "A.2.2",
  how: "Optional historical context showing that legislation without enforcement is ineffective. 'The Factory Act 1802 had no enforcement powers; the 1833 Act had only 4 inspectors for 4,000 mills. The parallel to our project: a risk register without enforcement mechanisms (geofence, kill switch, test gates) is similarly toothless.'",
  quote: "No legal powers of enforcement.",
  ref: "graham2023safety"
}
```

```
{
  id: RM-45,
  pri: MEDIUM,
  name: "Auditors Check Risk Assessments",
  src: "Graham Video 2 slide s07",
  sections: "B.7",
  how: "Mention to justify documentation rigour. 'Graham notes that reviewing risk assessments is one of the first things an auditor checks. Our risk register, flight day checklist, and pre-flight checks serve this audit function -- they provide evidence that safety was considered systematically, not ad hoc.'",
  quote: "Having a look at the risk assessments is one of the key things that an auditor does when they come round and visit your company.",
  ref: "graham2023risk"
}
```

---

## Priority Summary

| Priority | Count | IDs |
|----------|-------|-----|
| CRITICAL | 4 | RM-05, RM-07, RM-15, RM-22 |
| HIGH | 14 | RM-01, RM-02, RM-03, RM-04, RM-06, RM-09, RM-10, RM-14, RM-17, RM-18, RM-20, RM-31, RM-36, RM-42 |
| MEDIUM | 16 | RM-08, RM-11, RM-12, RM-13, RM-19, RM-21, RM-24, RM-25, RM-27, RM-28, RM-29, RM-32, RM-34, RM-35, RM-38, RM-40, RM-43, RM-45 |
| LOW | 11 | RM-16, RM-26, RM-30, RM-33, RM-37, RM-39, RM-41, RM-44 |

## Top 10 for D7 (if space-constrained)

1. **RM-05** -- f x c scoring with worked example (weather risk = 12, INTOLERABLE)
2. **RM-07** -- Risk compensation (NCNN speed + simulation overconfidence) = L4 self-critique
3. **RM-15** -- ALARP with quantitative reasoning (altitude trade-off)
4. **RM-22** -- Acknowledging solo risk assessment weakness = honest reflection
5. **RM-06** -- L/C framework mapped to geofence, kill switch, test ladder
6. **RM-17** -- Three pillars all applied to RC override guard decision
7. **RM-36** -- Iterative re-assessment after corrupt calibration file
8. **RM-09** -- HSE 5-step cycle mapped to concrete project actions
9. **RM-14** -- Criticality matrix with Intolerable threshold matching actual outcome
10. **RM-42** -- Critique of f x c independence assumption = L4 framework critique
