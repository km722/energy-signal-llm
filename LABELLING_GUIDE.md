# Labelling Guide for Handwritten Labels
## Two columns : `region` and `event_type`

### Part 1 : `region`
- The Guardian is a UK-based paper with global coverage
- We extracted 5 of the biggest economies in europe which serve as our target markets: UK, Germany, France, Spain, Netherlands

- **RULE 1**:  (`UK`, `Germany`, `France`, `Spain`, `Netherlands`) as labels

- **RULE 2**: Label "Europe" as `Europe`

- **RULE 3**: Label non–target european countries (not UK, Germany, France, Spain, Netherlands) or non-european countries as `other` to avoid confounding results of our targeted study.
    Examples: 
    Russia -> `other`
    US -> `other`

- **RULE 4**: Britain / Great Britain / England / Scotland / Wales / GB -> label `UK`. Holland -> `Netherlands`.

- **RULE 5**: **When** no country is named and the headline is about domestic life (bills, households, consumer advice and shopping, the grid, regulators, politics) -> `UK`. When no country is named and the story has no national subject at all (science studies, global markets, general explainers) -> `other`..

Example: "Energy bills to rise again in April" -> UK. 

Example: "Changes in solar energy fuelled high speed evolutionary changes, study suggests" -> `other`.

Example: "Energy bills to rise again in April" -> `UK`

- **RULE 6**: When a nationality adjective appears instead of a country name, label the matching country: British / English / Scottish / Welsh -> UK, French -> France, German -> Germany, Spanish -> Spain, Dutch -> Netherlands, European -> Europe.

Example: "British households face record winter bills" -> UK

- **RULE 7**: When a headline names more than one region, label the widest one that covers them.
If a target country and a bloc appear together, label Europe. Example: "Iran war threatens to delay large offshore wind projects in EU and UK" -> Europe.
If two or more target countries appear with no bloc, also label Europe. Example: "France and Germany agree emergency power sharing" -> Europe.
If a target country appears alongside a non-target country, label the target country, since that is the market we study. Example: "UK and China sign nuclear deal" -> UK.

### Part 2 : `event_type`
- **RULE 1**:  **When** the headline reports weather that happened or is happening (a heatwave, a storm, record sunshine), label the event type. **When** weather words appear only as industry/policy topics (wind farms, solar subsidies, "*wind power auction*"), **label** none. 
Value Types: {`heatwave`, `cold`, `storm`, `flood`, `drought`, `none`}
`cold`: cold snap, freeze, frost, ice, icy conditions, snow, blizzard, big freeze
`storm`: storm, gale, high winds, cyclone, hurricane, typhoon, tornado
`flood`: flooding, floods, deluge, burst rivers
`heatwave`: heatwave, extreme heat, record temperatures, scorcher
`drought`: drought, water shortage, hosepipe ban
`none`: none of the above

Example: "*Europe's heatwave drives electricity prices*" -> heatwave. Example: "*Record wind power auction proves doubters wrong*" -> none.

- **RULE 2**: **When** the headline asserts that a real weather event is happening or is
  forecast, **label** that event, whatever else the article is about. **When** the weather
  word is a name, a metaphor, or a policy term, **label** `none`. 
  **When** a season named without a specific event (this winter, summer bills) is not an event -> `none`.

Example: "Not cool: the air conditioning scams offering fake deals in the heatwave" -> `heatwave`
(the story is about fraud, but a real UK heatwave is happening)
Example: "Raise £12bn in budget by extending income tax thresholds freeze, says thinktank" -> `none`
(freeze is fiscal policy, not weather)
Example: "20 things to wear to stay warm this winter" -> seasonal, no event asserted -> `none`
"New year revellers told to wrap up warm with snow expected across UK" -> specific forecast asserted -> `cold`

- **RULE 3**: The event must be current or forecast. **When** the headline only refers back to
  a past event, **label** `none`. A flood that happened months ago does not move prices today.

Example: "Not cool: the air conditioning scams offering fake deals in the heatwave" -> `heatwave`
(happening now)
Example: "UK rejects visa for girl left destitute in Jamaica by Hurricane Melissa" -> `none`
(the hurricane is over; the story is about a visa decision)

The same applies to risk that has not happened: **when** the headline discusses weather risk,
planning, or defences with no event occurring or forecast, **label** `none`.

Example: "One in nine new homes in England built in areas of flood risk, study shows" -> `none`
(flood risk discussed; no flood is happening)
Example: "The Guardian view on heavy rain: England's flood defences are not strong enough" -> `none`
(about defences, not a current flood)
Example: "Floods could hit England while country is still in drought, forecasters say" -> `drought`
(drought is current; the floods are only possible)

- **RULE 4**: **When** a headline reports two weather events, **label** the one more likely to move
electricity demand or supply (heat and cold move demand hardest; storms and floods hit supply and
the grid). Not the first mentioned.

Example: "Two dead at Melbourne beach as wild wind batters state, while parts of Sydney hit by
record-breaking heat" -> `heatwave` (heat drives aircon demand; the wind is local damage)

