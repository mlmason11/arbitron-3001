import { useState } from "react"
import ArbitrageOpportunityCard from "./ArbitrageOpportunityCard"

export default function Nba() {

	const [arbitrageOpportunityList, setArbitrageOpportunityList] = useState({})

	async function getNbaArbitrageOpportunities() {
		const response = await fetch(`/recipes`)
    	const recipes = await response.json()
    	return response.ok
        	? {recipes}
        	: new Response("", { status: response.status, statusText: "Could not find the recipes" })
	}

	return (
		<div>
			<h1>NBA</h1>
		</div>
	)
}