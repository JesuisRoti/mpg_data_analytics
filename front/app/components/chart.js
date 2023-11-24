"use client";
import React, { useState, useEffect } from "react";
import Select from "react-select";
import {
	Chart as ChartJS,
	ArcElement,
	Tooltip,
	Legend,
	CategoryScale,
	LinearScale,
	BarElement,
	PointElement,
} from "chart.js";
import { Scatter } from "react-chartjs-2";
import styles from "./layout.module.css";

// Register the required components for ChartJS
ChartJS.register(
	ArcElement,
	Tooltip,
	Legend,
	CategoryScale,
	LinearScale,
	BarElement,
	PointElement,
);

function MyChart() {
	const api = "http://localhost:5001/top_players";
	const [topNumber, setTopNumber] = useState(10);
	const [datasetData, setDatasetData] = useState([]);
	const [col_x, setCol_x] = useState("totalGoals");
	const [col_y, setCol_y] = useState("averageRating");
	const [colCriteria, setColCriteria] = useState("averagePoints");
	const [playersData, setPlayersData] = useState([]);
	const [chartData, setChartData] = useState({
    	labels: [],
    	datasets: [],
  	});
	const [position, setPosition] = useState({
		A: false,
		M: false,
		D: false,
		G: false,
	});

  	const [rankingColumn, setRankingColumn] = useState({
		totalGoals: false,
		averagePoints: false,
		averageRating: false,
		quotation: false,
		participation: false,
  	});
  
  	const options = {
	  	plugins: {
		  	legend: {
				  display: true,
			},
    	},
		title: {
      		display: true,
			text: "Scatter Plot Example",
			position: "bottom",
		},
		scales: {
			  y: {
				  title: {
					  display: true,
					  text: col_y,
				  },
			  },
			x: {
				  title: {
					  display: true,
					  text: col_x,
				  },
			},
		},
		maintainAspectRatio: false,
	};
	const colXOptions = Object.keys(rankingColumn).map((key) => ({
		value: key,
		label: key,
	}));
	
	const positionOptions = Object.keys(position).map((key) => ({
		value: key,
		label: key,
	}));
	
	const rankingColumnOptions = Object.keys(rankingColumn).map((key) => ({
		value: key,
		label: key,
	}));
	
	async function fetchData() {
		try {
			const response = await fetch(api + "?top_number=10");
			const data = await response.json();
			setPlayersData(data);
			setChartData(createChartData(data));
		} catch (error) {
			console.error("Error fetching data: ", error);
		}
	}
	
	function getRandomColor() {
		const letters = "0123456789ABCDEF";
		let color = "#";
		for (let i = 0; i < 6; i++) {
			color += letters[Math.floor(Math.random() * 16)];
		}
		return color;
	}
	
	function createChartData(data) {
		const datasets = [];
		for (let el of data) {
			const color = getRandomColor();
			datasets.push({
				label: el["playerFullName"],
				data: [{ x: el[col_x], y: el[col_y] }],
				backgroundColor: color,
				borderColor: color,
				borderWidth: 1,
				pointStyle: "circle",
				pointRadius: 5,
			});
		}
		console.log(datasets);
		setDatasetData(datasets);
		return {
			datasets: datasets,
		};
	}
	
	function modifyPosition(e) {
		const newPosition = {
			A: false,
    		M: false,
    		D: false,
    		G: false,
  		};
		
		for (const el of e) {
			newPosition[el["value"]] = true;
		}
		setPosition(newPosition);
	}
	
	function modifyRankingColumn(e) {
		setColCriteria(e.label);
	}
	
	async function fetchDataWithParams(params) {
		try {
			const response = await fetch(api + "?" + params.toString());
			const data = await response.json();
			setPlayersData(data);
			setChartData(createChartData(data));
		} catch (error) {
			console.error("Error fetching data: ", error);
		}
	}
	
	useEffect(() => {
		const params = new URLSearchParams();
		let positionsParams = "";
		Object.keys(position).forEach((key) => {
			if (position[key]) {
				console.log(key)
        		// params to string send every position in the url as position=X&position=Y so concatenate
        		// a string to receive the data correctly in the backend
        		if (positionsParams.length > 0) {
					positionsParams += `,${key}`;
				} else {
					positionsParams += key;
				}
			}
		});
		params.append("position", positionsParams);
		params.append("ranking_criteria", colCriteria);
		params.append("top_number", topNumber.toString());
		fetchDataWithParams(params);
  	}, [position, colCriteria]);

	useEffect(() => {
		setChartData(createChartData(playersData));
	}, [col_x, col_y]);

	useEffect(() => {
		fetchData();
  	}, []);
	
	return (
		<div style={{ height: "600px" }}>
			<div className={styles.optionsContainer}>
				<h3 className={styles.title}>Options :</h3>
				<div className={styles.selectRow}>
					<div className="selectRowContainer">
						<p className={styles.selectTitle}>Position</p>
						<Select
							options={positionOptions}
							isMulti={true}
							onChange={(e) => modifyPosition(e)}
							className="my-react-select"
						/>
					</div>
					<div className="selectRowContainer">
						<p className={styles.selectTitle}>Ranking Criteria</p>
						<Select
							options={rankingColumnOptions}
							isMulti={false}
							onChange={(e) => modifyRankingColumn(e)}
							className="my-react-select"
						/>
					</div>
					<div className="selectRowContainer">
						<p className={styles.selectTitle}>Column X</p>
						<Select
							options={colXOptions}
							isMulti={false}
							onChange={(e) => setCol_x(e.label)}
							className="my-react-select"
						/>
					</div>
          			<div className="selectRowContainer">
            			<p className={styles.selectTitle}>Column Y</p>
            			<Select
							options={colXOptions}
							isMulti={false}
							onChange={(e) => setCol_y(e.label)}
							className="my-react-select"
						/>
					</div>
				</div>
			</div>
			{<Scatter data={chartData} options={options} />}
		</div>
	);
}

export default MyChart;
