$.when($.ready).then(async function() {
	const url = "http://localhost:9000/allanime"
	try {
		const response = await fetch(url);
		if (!response.ok) {
		  throw new Error(`Response status: ${response.status}`);
		}
		
		const result = await response.json();
		
		table = $("#animetable");
		headerRow = $("<tr>");
		for (let col = 0; col < result["message"]["columns"].length; col++) {
			let headerLabel = result["message"]["columns"][col];
			headerRow.append($(`<th>${headerLabel}</th>`));
		}
		headerRow.append($("<th>Edit/View</th>"));
		table.append(headerRow);
		
		for (let row = 0; row < result["message"]["rows"].length; row++) {
			rowElem = $("<tr>");
			for (let col = 0; col < result["message"]["rows"][row].length; col++) {
				let cellData = result["message"]["rows"][row][col];
				rowElem.append($(`<td>${cellData}</td>`));
			}
			rowElem.append($(`<td><a href='/neweditanime.html?animeid=${result["message"]["rows"][row][0]}'>Edit/View</a></td>`))
			table.append(rowElem);
		}
	} catch (error) {
		console.error(error.message);
	}
});