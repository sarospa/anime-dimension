displayRows = {
	"Name": {displayName: "Name", width: "35%"},
	"Notes": {displayName: "Notes", width: "60%"}
}
columns = [];
data = [];
notesLimit = 100;

$.when($.ready).then(async function() {
	const url = `${baseURL}/series`
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
	let table = $("#seriestable");
	table.empty();
	
	let headerRow = $("<tr>");
	for (let col = 0; col < columns.length; col++) {
		let columnName = columns[col];
		if (Object.keys(displayRows).includes(columnName)) {
			headerRow.append($(`<th style='width: ${displayRows[columnName].width}'>${displayRows[columnName].displayName}</th>`));
		}
	}
	table.append(headerRow);
	
	let titleIndex = columns.findIndex((col) => col === "Name");
	
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
					if (columnName === "Notes" && cellData.length >= notesLimit) {
						cellData = cellData.substring(0, notesLimit) + "...";
					}
					else if (columnName === "Name") {
						cellData = `<a href="/neweditseries.html?seriesid=${data[row][0]}">${cellData}</a>`
					}
					if (cellData === null) cellData = "";
					rowElem.append($(`<td>${cellData}</td>`));
				}
			}
			table.append(rowElem);
		}
	}
}