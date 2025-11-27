animeId = null;
tagList = [];
allTags = [];
extrasList = [];
localExtraId = 0;

$.when($.ready).then(async function() {
	try {
		const urlParams = new URLSearchParams(window.location.search);
		animeId = urlParams.get('animeid');
		
		if (animeId === null) {
			$("#submitButton").html("Create");
		}
		
		const sourcesResponse = await fetch(`${baseURL}/sources`);
		if (!sourcesResponse.ok) {
		  throw new Error(`Response status: ${sourcesResponse.status}`);
		}
		
		const sources = await sourcesResponse.json();
		
		let sourceDropdown = $("#source");
		for (let row = 0; row < sources["message"]["rows"].length; row++) {
			let rowData = sources["message"]["rows"][row]
			sourceDropdown.append($(`<option value='${rowData[0]}'>${rowData[1]}</option>`))
		}
		
		const tagsResponse = await fetch(`${baseURL}/tags`);
		if (!tagsResponse.ok) {
			throw new Error(`Response status: ${tagsResponse.status}`);
		}
		
		const tagsData = await tagsResponse.json();
		allTags = tagsData["message"]["rows"];
		
		const seriesResponse = await fetch(`${baseURL}/series`);
		if (!seriesResponse.ok) {
			throw new Error(`Response status: ${seriesResponse.status}`);
		}
		
		const seriesData = await seriesResponse.json();
		
		let seriesDropdown = $("#series");
		for (let row = 0; row < seriesData["message"]["rows"].length; row++) {
			let rowData = seriesData["message"]["rows"][row];
			seriesDropdown.append($(`<option value='${rowData[0]}'>${rowData[1]}</option>`))
		}
		
		const partnersResponse = await fetch(`${baseURL}/watchpartners`);
		if (!partnersResponse.ok) {
			throw new Error(`Response status: ${partnersResponse.status}`);
		}
		
		const partnersData = await partnersResponse.json();
		
		let watchContainer = $("#watchContainer");
		for (let row = 0; row < partnersData["message"]["rows"].length; row++) {
			let rowData = partnersData["message"]["rows"][row];
			watchContainer.append($(`<button onclick="watchAnime(${rowData[0]})">Watch with ${rowData[1]}</button>`));
		}
		
		if (animeId !== null) {
			const animeResponse = await fetch(`${baseURL}/anime/${animeId}`);
			if (!animeResponse.ok) {
			  throw new Error(`Response status: ${animeResponse.status}`);
			}
			
			const anime = await animeResponse.json();
			
			let cols = anime["message"]["anime"]["columns"];
			let rows = anime["message"]["anime"]["rows"];
			
			let title = rows[0][cols.findIndex((col) => col === "Title")];
			$("#title").val(title);
			
			let notes = rows[0][cols.findIndex((col) => col === "Notes")];
			$("#notes").val(notes);
			
			let review = rows[0][cols.findIndex((col) => col === "Review")];
			$("#review").val(review);
			
			let yuriRating = rows[0][cols.findIndex((col) => col === "YuriRatingId")];
			$("#yuriRating").val(yuriRating);
			
			let releaseDate = rows[0][cols.findIndex((col) => col === "ReleaseDate")];
			$("#releaseDate").val(releaseDate);
			
			let lastSeason = rows[0][cols.findIndex((col) => col === "LastSeason")];
			$("#lastSeason").val(lastSeason);
			
			let lastEpisode = rows[0][cols.findIndex((col) => col === "LastEpisode")];
			$("#lastEpisode").val(lastEpisode);
			
			let sourceId = rows[0][cols.findIndex((col) => col === "SourceId")];
			$("#source").val(sourceId);
			
			let priority = rows[0][cols.findIndex((col) => col === "Priority")];
			$("#priority").val(priority);
			
			let seriesId = rows[0][cols.findIndex((col) => col === "SeriesId")];
			$("#series").val(seriesId);
			
			let tagCols = anime["message"]["tags"]["columns"];
			tagList = anime["message"]["tags"]["rows"];
			
			let tagsDiv = $("#tags");
			for (let i = 0; i < tagList.length; i++) {
				tagsDiv.append($(`<span class='tag' id='tag-${tagList[i][0]}'>${tagList[i][1]} <button onclick='deleteTag(${tagList[i][0]})'>X</button></span>`));
			}
			
			extrasList = anime["message"]["extras"]["rows"];
			for (let i = 0; i < extrasList.length; i++) {
				addExtraHtml(i, extrasList[i][2]);
			}
			localExtraId = extrasList.length;
		}
		
		populateTagDropdown();
		
	} catch (error) {
		console.error(error.message);
	}
});

function deleteTag(tagId) {
	tagList = tagList.filter((tag) => tag[0] !== tagId);
	$(`#tag-${tagId}`).remove();
	populateTagDropdown();
}

function deleteExtra(id) {
	if (confirm(`Delete ${extrasList[id][2]}?`)) {
		delete extrasList[id]
		$(`#extra-${id}`).remove();
	}
}

function addTag() {
	let tagId = $("#selectTags").val();
	let newTag = allTags.find((tag) => tag[0] == tagId);
	tagList.push(newTag);
	let tagsDiv = $("#tags");
	tagsDiv.append($(`<span class='tag' id='tag-${newTag[0]}'>${newTag[1]} <button onclick='deleteTag(${newTag[0]})'>X</button></span>`));
	populateTagDropdown();
}

function addExtra() {
	extraDesc = $("#newExtraText").val();
	if (extraDesc.length > 0) {
		$("#newExtraText").val("");
		extrasList[localExtraId] = [null, animeId, extraDesc];
		let extrasDiv = $("#extras");
		addExtraHtml(localExtraId, extraDesc);
		localExtraId += 1;
	}
}

function addExtraHtml(id, desc) {
	let extrasDiv = $("#extras");
	extrasDiv.append($(`
		<span class='extra' id='extra-${id}'>
			<span id='extra-display-${id}'>${desc}</span>
			<input id='extra-input-${id}' type='text' style='display:none'/> 
			<button id='extra-edit-${id}' onclick='editExtra(${id})'>Edit</button>
			<button id='extra-save-${id}' style='display:none' onclick='saveExtra(${id})'>Save</button>
			<button onclick='deleteExtra(${id})'>X</button></span>`));
	$(`#extra-input-${id}`).val(desc);
}

function editExtra(id) {
	$(`#extra-display-${id}`).hide();
	$(`#extra-edit-${id}`).hide();
	$(`#extra-input-${id}`).show();
	$(`#extra-save-${id}`).show();
}

function saveExtra(id) {
	let display = $(`#extra-display-${id}`);
	let input = $(`#extra-input-${id}`);
	let editButton = $(`#extra-edit-${id}`);
	let saveButton = $(`#extra-save-${id}`);
	display.text(input.val());
	extrasList[id][2] = input.val();
	display.show();
	editButton.show();
	input.hide();
	saveButton.hide();
}

function populateTagDropdown() {
	let otherTags = allTags.filter((tagA) => !tagList.find((tagB) => tagA[0] === tagB[0]))
	tagDropdown = $("#selectTags");
	tagDropdown.empty();
	for (let row = 0; row < otherTags.length; row++) {
		let rowData = otherTags[row]
		tagDropdown.append($(`<option value='${rowData[0]}'>${rowData[1]}</option>`))
	}
	if (otherTags.length === 0) {
		$("#tagControls").hide();
	}
	else {
		$("#tagControls").show();
	}
}

function watchAnime(watchPartnerId) {
	window.location.href = `/neweditwatchthrough.html?animeid=${animeId}&partnerid=${watchPartnerId}`;
}

async function submitAnime() {
	let title = $("#title").val();
	let notes = $("#notes").val();
	let review = $("#review").val();
	let yuriRating = $("#yuriRating").val();
	let releaseDate = new Date($("#releaseDate").val());
	let lastSeason = parseInt($("#lastSeason").val());
	let lastEpisode = parseInt($("#lastEpisode").val());
	let source = $("#source").val()
	let priority = $("#priority").val();
	let seriesId = $("#series").val();
	
	let errorMessage = '';
	
	if (!title || title.length === 0) errorMessage += "Title cannot be empty.\r\n";
	if (isNaN(lastSeason)) errorMessage += "Last season must be a valid number.\r\n";
	if (isNaN(lastEpisode)) errorMessage += "Last episode must be a valid number.\r\n";
	if (releaseDate.toString() === "Invalid Date") errorMessage += "Release date must be a valid date.\r\n";
	
	if (errorMessage.length > 0) {
		alert(errorMessage);
		return;
	}
	
	requestBody = {
		"animeId": animeId,
		"title": title,
		"notes": notes,
		"review": review,
		"releaseDate": releaseDate.toISOString().split('T')[0],
		"lastSeason": lastSeason,
		"lastEpisode": lastEpisode,
		"source": parseInt(source),
		"priority": parseInt(priority),
		"tags": tagList.map((tag) => tag[0]),
		"extras": extrasList.filter((_) => true) // to get the indexes lined up properly since I'm handling deleting extras in a fucky way
	};
	if (yuriRating) requestBody["yuriRating"] = parseInt(yuriRating);
	if (seriesId) requestBody["seriesId"] = parseInt(seriesId);
	
	const saveRequest = new Request(`${baseURL}/saveanime`, {
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
	
	window.location.href = "/";
}