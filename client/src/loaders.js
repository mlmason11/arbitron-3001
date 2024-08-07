export async function getArbitrageOpportunities() {
	const response = await fetch(`/recipes`)
	const recipes = await response.json()
	return response.ok
		? {recipes}
		: new Response("", { status: response.status, statusText: "Could not find the recipes" })
}