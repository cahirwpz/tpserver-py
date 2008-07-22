Adding New Research:
	To add new researches they should be added to the csv file.
	 Each research type has its own csv fiile.
	Researches all have the following common attributes:
		Name
			Names are the proper names that will be displayed when a player is researching 	
		Abbreviations
			Abbreviations are used for requirements and some other internal measures.
			They should try to reflect their normal names.
		Cost
			Number of credits total needed to be devoted in order to finish researching.
		Requirements 
			The researches that a user must complete before this one becomes available.
			Requirements should be written as abbreviations separated by commas

		Name and Abbreviations should be unique.

Each Type of Research has additional data that must be given:
	
	Note: Ratio Percentages should be written as decimals. Ex. 0.10 = 10% Bonus	

	Combat: Combat Researches affect unit attributes in all things related to combat. It contains the 
	following  additional atttributes:
		Damage:
			 How much damage is added to each unit for this research.
		Number of Attacks: 
			How many attacks are added to each unit for this research.
		Health:
			 How much more health each drone will have from this research.
		Types: 
			The Ship types that might be affected by this research. 
		Ships: 
			Any individual drones that could also be affected by this research not falling into 			the given types.

	Economy: Economy Researches affect all planet orders in this case Research and Produce 		Drones.
		Resource:
			Resources to be added to each planet
		Resource Ratio:
			Percentage Bonus of produced resources to be added to each planet.
		Research Ratio:
			Bonus Resources are added from the given credits to a Research production cost.
		Research Type:
			What researches are affected by the bonuses of this upgrade.
		Drone Cost
			Amount of resources each drone's cost will be reduced by.
		Drone Cost Ratio
			Percentage reduction of drone costs.
		Drone Types:
			Drone Types that are affected by the reduced cost
		Drone Ships:
			Individual Drones affected by the reduced cost not in the Drone Types given.

	World: World Researches affect drones in any way that is not related to combat. ie. Capturing 	and movement speed.
		Speed: 
			Increase Speed by a fixed amount
		Speed Ratio:
			Increase Speed by a bonus percentage. 
		Power:
			Increase each Drones power by a fixed amount
		Unit Affected:
			Ships that are affected by the research.
		Types Affected:
			Ship Types affected by the research.

	Unit: Unit Researches allow for new units to be unlocked for production. They contain only one 	extra attribute:
		Ships: Contains the ship this research unlocks. It should be a ships full name.

	Note: On Units: The Drone CSV file must be updated for the ship to include the research's 	abbreviation in its requirements field.
