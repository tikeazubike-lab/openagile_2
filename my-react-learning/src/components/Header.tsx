import Globe from "../assets/globe.png"

export default function Header(){
    return (
        <header>
            <img src={Globe} alt="Globe" />
            <h1>my travel journal</h1>
        </header>
    )
}