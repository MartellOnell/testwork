import logo from "./svg/logo.svg"
import marsButtonBox from "./svg/marsButtonBox.svg"
import marsText from "./svg/marsText.svg"
import activeBox from "./svg/activeBox.svg"
import nonactiveBox from "./svg/nonactiveBox.svg"
import { hydrateRoot } from "react-dom/client"

export const Landing = () => {
    return (
        <div>

        </div>
    )
}

const NavBar = () => {
    return (
        <nav>
            <img src={logo} alt="logo" />
            <div className="nav-box">
                <a href="">Главная</a>
                <a href="">Технология</a>
                <a href="">График полётов</a>
                <a href="">Гарантии</a>
                <a href="">О компании</a>
                <a href="">Контакты</a>
            </div>
        </nav>
    )
}

const MainFrame = () => {
    return (
        <div>
            <img src={marsText} alt="mars text" />

            <button>
                <img src={marsButtonBox} alt="marsButtonBox" />
                <p>Начать Путешествие</p>
            </button>

            <div>
                <InfoBox /> {/*add params*/}
                <InfoBox />
                <InfoBox />
                <InfoBox />
             </div>
        </div>
    )
}

const InfoBox = ({contentFetch, rotate, content}) => { //make hover
    return (
        <div>
            <img src={nonactiveBox} alt="" style={{
                rotate: `${rotate}deg`
            }} />
            <p>{content.text1}</p>
            <div>
                {
                    content.type == "percent" ?
                    <h1>{contentFetch}%</h1> :
                    content.type == "year" ?
                    <h1>{contentFetch}<span>г.</span></h1> :
                    <h1>{contentFetch}</h1>
                }
            </div>
            <p>{content.text2}</p>
        </div>
    )
}