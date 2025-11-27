seriesId = null;

$.when($.ready).then(async function() {
	try {
		const urlParams = new URLSearchParams(window.location.search);
		seriesId = urlParams.get('seriesid');
		
		if (seriesId === null) {
			$("#submitButton").html("Create");
		}
		else {
			const seriesResponse = await fetch(`${baseURL}/series/${seriesId}`);
			if (!seriesResponse.ok) {
			  throw new Error(`Response status: ${seriesResponse.status}`);
			}
			
			const series = await seriesResponse.json();
			
			let cols = series["message"]["columns"];
			let rows = series["message"]["rows"];
			
			let name = rows[0][cols.findIndex((col) => col === "Name")];
			$("#name").val(name);
			
			let animeInSeries = rows[0][cols.findIndex((col) => col === "AnimeInSeries")].split("|");
			let animeList = $("#animeInSeries");
			for (let i = 0; i < animeInSeries.length; i++) {
				animeList.append($(`<li>${animeInSeries[i]}</li>`));
			}
			
			let notes = rows[0][cols.findIndex((col) => col === "Notes")];
			$("#notes").val(notes);
		}
	} catch (error) {
		console.error(error.message);
	}
});

async function submitSeries() {
	let name = $("#name").val();
	let notes = $("#notes").val();
	
	let errorMessage = '';
	
	if (!name || name.length === 0) errorMessage += "Name cannot be empty.\r\n";
	
	if (errorMessage.length > 0) {
		alert(errorMessage);
		return;
	}
	
	requestBody = {
		"seriesId": seriesId,
		"name": name,
		"notes": notes
	}
	
	const saveRequest = new Request(`${baseURL}/saveseries`, {
		method: "POST",
		body: JSON.stringify(requestBody),
		headers: {                   
			'Content-Type': 'application/json',
		}
	});
	
	const saveResponse = await fetch(saveRequest);
	if (!saveResponse.ok) {
		throw new Error(`Response status: ${saveResponse.status}`);
	}
	
	window.location.href = "/allseries.html";
}