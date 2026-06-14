import FunImage from "../assets/react.svg";
import './FunFacts.css';

function FunFacts() {
    return (
        <section className="fun-facts-card">
            <header className="fun-facts-header">
                <img src={FunImage} alt="React Logo" className="fun-facts-logo" />
            </header>
            <h1 className="fun-facts-title">Fun facts about React</h1>
            <ul className="fun-facts-list">
                <li className="fun-facts-item">Was first released in 2013</li>
                <li className="fun-facts-item">Was originally created by Jordan Walke</li>
                <li className="fun-facts-item">Has well over 100K stars on Github</li>
                <li className="fun-facts-item">Is maintained by Meta</li>
                <li className="fun-facts-item">Powers thousands of enterprise apps, including mobile apps</li>
            </ul>
        </section>
    );
}

export default FunFacts;
            