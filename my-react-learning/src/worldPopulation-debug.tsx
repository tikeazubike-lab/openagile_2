import type { PopulationData } from "./assets/population";

export default function WorldPopulation(props: PopulationData){
    // DEBUGGING: Understanding how props are received after destructuring
    console.log("\n--- Inside WorldPopulation Component ---")
    console.log("9. 'props' received:", props)
    console.log("10. props is an object with", Object.keys(props).length, "properties")
    console.log("11. props.country:", props.country)
    console.log("12. props.pop2023:", props.pop2023)
    console.log("13. props.rank:", props.rank)
    console.log("14. All props keys:", Object.keys(props))
    console.log("--- End WorldPopulation Component ---\n")

    return (
        <article className="population-entry">
            <div className="info-container">
                <h2 className="country-name">{props.country}</h2>
                <div className="stats-grid">
                    <div className="stat-item">
                        <span className="stat-label">Rank:</span>
                        <span className="stat-value">#{props.rank}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">2023 Population:</span>
                        <span className="stat-value">{props.pop2023.toLocaleString()}</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Growth Rate:</span>
                        <span className="stat-value">{(props.growthRate * 100).toFixed(2)}%</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">World Share:</span>
                        <span className="stat-value">{(props.worldPercentage * 100).toFixed(2)}%</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Density:</span>
                        <span className="stat-value">{props.density.toFixed(2)} per km²</span>
                    </div>
                    <div className="stat-item">
                        <span className="stat-label">Net Change:</span>
                        <span className="stat-value">{props.netChange.toFixed(4)}</span>
                    </div>
                </div>
                <div className="historical-data">
                    <h3>Historical Population</h3>
                    <ul>
                        <li>1980: {props.pop1980.toLocaleString()}</li>
                        <li>2000: {props.pop2000.toLocaleString()}</li>
                        <li>2010: {props.pop2010.toLocaleString()}</li>
                        <li>2022: {props.pop2022.toLocaleString()}</li>
                    </ul>
                </div>
                <div className="projections">
                    <h3>Projections</h3>
                    <ul>
                        <li>2030: {props.pop2030.toLocaleString()}</li>
                        <li>2050: {props.pop2050.toLocaleString()}</li>
                    </ul>
                </div>
                <div className="area-info">
                    <h3>Area Information</h3>
                    <ul>
                        <li>Total Area: {props.area.toLocaleString()} km²</li>
                        <li>Land Area: {props.landAreaKm.toLocaleString()} km²</li>
                    </ul>
                </div>
            </div>
        </article>
    )
}
