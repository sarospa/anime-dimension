watchthroughId = null;
animeId = null;
partnerId = null;
animeExtras = [];

$.when($.ready).then(async function() {
	try {
		const urlParams = new URLSearchParams(window.location.search);
		animeId = urlParams.get('animeid');
		partnerId = urlParams.get('partnerid');
		
		const watchthroughResponse = await fetch(`${baseURL}/watchthrough/${animeId}/${partnerId}`);
		if (!watchthroughResponse.ok) {
		  throw new Error(`Response status: ${watchthroughResponse.status}`);
		}
		
		const watchthrough = await watchthroughResponse.json();
		
		let cols = watchthrough["message"]["columns"];
		let rows = watchthrough["message"]["rows"];
		
		watchthroughId = rows[0][cols.findIndex((col) => col === "WatchthroughId")];
		
		let title = rows[0][cols.findIndex((col) => col === "AnimeTitle")];
		let watchPartner = rows[0][cols.findIndex((col) => col === "WatchPartner")];
		$("#animeHeader").text(`${title} with ${watchPartner}`);
		
		let active = rows[0][cols.findIndex((col) => col === "IsActive")];
		$("#active").prop("checked", active);
		
		let forceComplete = rows[0][cols.findIndex((col) => col === "ForceComplete")];
		$("#forceComplete").prop("checked", forceComplete);
		
		let season = rows[0][cols.findIndex((col) => col === "Season")];
		$("#season").val(season);
		
		let episode = rows[0][cols.findIndex((col) => col === "Episode")];
		$("#episode").val(episode);
		
		let extras = $("#extras");
		for (let i = 0; i < rows.length; i++) {
			let animeExtra = rows[i][cols.findIndex((col) => col === "AnimeExtra")]
			let animeExtraId = rows[i][cols.findIndex((col) => col === "AnimeExtraId")]
			let extraWatched = rows[i][cols.findIndex((col) => col === "ExtraWatched")]
			if (animeExtraId) {
				animeExtras.push(animeExtraId);
				extras.append($(`<div><input type='checkbox' id='extra-${animeExtraId}' /> <label>${animeExtra}</label></div>`));
				$(`#extra-${animeExtraId}`).prop("checked", extraWatched);
			}
		}
	} catch (error) {
		console.error(error.message);
	}
});

async function submitWatchthrough() {
	if (!watchthroughId) {
		alert("Error: No watchthrough ID.");
		return;
	}
	
	let isActive = $("#active").prop("checked");
	let forceComplete = $("#forceComplete").prop("checked");
	let season = $("#season").val();
	let episode = $("#episode").val();
	let completedExtras = [];
	for (let i = 0; i < animeExtras.length; i++) {
		if ($(`#extra-${animeExtras[i]}`).prop("checked")) {
			completedExtras.push(animeExtras[i]);
		}
	}
	
	let errorMessage = '';
	
	if (isNaN(season)) errorMessage += "Season must be a valid number.\r\n";
	if (isNaN(episode)) errorMessage += "Episode must be a valid number.\r\n";
	
	if (errorMessage.length > 0) {
		alert(errorMessage);
		return;
	}
	
	requestBody = {
		"watchthroughId": watchthroughId,
		"isActive": isActive,
		"forceComplete": forceComplete,
		"season": season,
		"episode": episode,
		"completedExtras": completedExtras
	}
	
	const saveRequest = new Request(`${baseURL}/updatewatchthrough`, {
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
	
	window.location.href = `/neweditanime.html?animeid=${animeId}`;
}

function returnToAnime() {
	window.location.href = `/neweditanime.html?animeid=${animeId}`;
}