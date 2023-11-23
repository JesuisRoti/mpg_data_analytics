'use client'
import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from "chart.js";
import { Chart } from 'react-chartjs-2';
import styles from './layout.module.css';

// Register the required components for ChartJS
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

function MyChart() {
    const [playersData, setPlayersData] = useState([]);
    const [chartData, setChartData] = useState({
        labels: [],
        datasets: []
    });
    const [position, setPosition] = useState({
        'A': false,
        'M': false,
        'D': false,
        'G': false
    });

    const [rankingColumn, setRankingColumn] = useState({
        'totalGoals': false,
        'averagePoints': false,
        'averageRating': false,
        'quotation': false,
        'participation': false
    });

    useEffect(() => {
        fetchData();
    }, []);


    // Function to fetch data
    async function fetchData() {
        try {
            const response = await fetch('http://10.103.8.27:5001/top_forward?top_number=10');
            const data = await response.json();
            setPlayersData(data);
            setChartData(createChartData(data));
        } catch (error) {
            console.error('Error fetching data: ', error);
        }
    }

    function createChartData(data) {
        const dfKeys = Object.keys(data[0])
        return {
            labels: data.map(item => item.playerFullName),
            datasets: [
                {
                    label: 'Total Goals',
                    data: data.map(item => item.totalGoals),
                    backgroundColor: 'rgba(255, 99, 132, 0.5)',
                },
                {
                    label: 'Average Rating',
                    data: data.map(item => item.averageRating),
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                }
            ]
        };
    }

    function modifyPosition(e, key) {
        setPosition({
            ...position,
            [key]: e.target.checked
        })
    }

    function modifyRankingColumn(e, key) {
        setRankingColumn({
            ...rankingColumn,
            [key]: e.target.checked
        })
    }

    useEffect(() => {
        console.log(position);
        console.log(rankingColumn);
    }, [position, rankingColumn]);

    return (
        <div>
            <div className={styles.optionsContainer}>
                <h3 className={styles.title}>Options :</h3>
                <div className={styles.optionsRow}>
                    <label className={styles.label}>
                        Forward
                        <input
                            onChange={e => modifyPosition(e, 'A')}
                            type="checkbox"
                        />
                    </label>
                    <label className={styles.label}>
                        MidFielder
                        <input
                            onChange={e => modifyPosition(e, 'M')}
                            type="checkbox"
                        />
                    </label>
                    <label className={styles.label}>
                        FullBack
                        <input
                            onChange={e => modifyPosition(e, 'D')}
                            type="checkbox"
                        />
                    </label>
                    <label className={styles.label}>
                        Goal keepers
                        <input
                            onChange={e => modifyPosition(e, 'G')}
                            type="checkbox"
                        />
                    </label>
                </div>
                <div className={styles.optionsRow}>
                   {Object.keys(rankingColumn).map(key => (
                    <label key={key} className={styles.label}>
                        {key}
                        <input
                            onChange={e => modifyRankingColumn(e, key)}
                            type="checkbox"
                        />
                    </label>

                   ))}
                </div>
            </div>
            {/*{chartData.labels.length > 0 && <Chart type='bar' data={chartData} />}*/}
        </div>
    )
}

export default MyChart;
