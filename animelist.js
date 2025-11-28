displayRows = {
	"Title": {displayName: "Title", width: "35%"},
	"Notes": {displayName: "Notes", width: "30%"},
	"YuriRatingId": {displayName: "Yuri Rating", width: "5%"},
	"ReleaseDate": {displayName: "Release Date", width: "5%"},
	"LastEpisode": {displayName: "Last Episode", width: "5%"},
	"Source": {displayName: "Source", width: "5%"},
	"Priority": {displayName: "Priority", width: "5%"}
}
columns = [];
data = [];

$.when($.ready).then(async function() {
	const url = `${baseURL}/allanime`
	try {
		const response = await fetch(url);
		if (!response.ok) {
		  throw new Error(`Response status: ${response.status}`);
		}
		
		const result = await response.json();
		columns = result["message"]["columns"];
		data = result["message"]["rows"]
		
		buildTable();
	} catch (error) {
		console.error(error.message);
	}
});

function buildTable(titleSearch) {
	let table = $("#animetable");
	table.empty();
	
	let headerRow = $("<tr>");
	for (let col = 0; col < columns.length; col++) {
		let columnName = columns[col];
		if (Object.keys(displayRows).includes(columnName)) {
			headerRow.append($(`<th style='width: ${displayRows[columnName].width}'>${displayRows[columnName].displayName}</th>`));
		}
	}
	table.append(headerRow);
	
	let titleIndex = columns.findIndex((col) => col === "Title");
	
	let isEven = true;
	for (let row = 0; row < data.length; row++) {
		if (!titleSearch || data[row][titleIndex].toLowerCase().includes(titleSearch)) {
			let parity = isEven ? "even" : "odd"
			isEven = !isEven;
			let rowElem = $(`<tr class='${parity}'>`);
			for (let col = 0; col < data[row].length; col++) {
				let columnName = columns[col];
				if (Object.keys(displayRows).includes(columnName)) {
					let cellData = data[row][col];
					if (columnName === "Notes" && cellData.length >= 50) {
						cellData = cellData.substring(0, 50) + "...";
					}
					else if (columnName === "Title") {
						cellData = `<a href="/neweditanime.html?animeid=${data[row][0]}">${cellData}</a>`
					}
					if (cellData === null) cellData = "";
					rowElem.append($(`<td>${cellData}</td>`));
				}
			}
			table.append(rowElem);
		}
	}
}

function textSearch() {
	buildTable($("#titleSearch").val().toLowerCase());
}

async function navigateToRandomAnime() {
	const response = await fetch(`${baseURL}/randomanime`);
	if (!response.ok) {
	  throw new Error(`Response status: ${response.status}`);
	}
	
	const result = await response.json();
	window.location.href = `/neweditanime.html?animeid=${result["message"]}`
}