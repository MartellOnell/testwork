import logo from "./png/logo.png"
import marsButtonBox from "./svg/marsButtonBox.svg"
import planet from "./png/planet.png"
import pointMars from "./png/pointMars.png"
import xImg from "./png/x.png"
import "./index.css"
import MediaQuery from 'react-responsive'
import { motion } from "framer-motion"
import { useState } from "react"

export const Landing = () => {
    return (
        <div>
            <NavBar />
            <MainFrame />
        </div>
    )
}

const NavBar = () => {
    const [isOpen, set] = useState(false)
    return (
        <>
            <MediaQuery minWidth={1399}>
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
            </MediaQuery>
            <MediaQuery maxWidth={1399}>
                <motion.nav
                    initial={false}
                    animate={ isOpen ? "open" : "close"}
                >
                    <MediaQuery minWidth={768}>
                        <img src={logo} alt="logo" />
                    </MediaQuery>
                    <MediaQuery maxWidth={767}>
                        <div className="logo-wrap">
                            <img src={xImg} alt="" style={{width: "64.84px", height: "20px"}}/>
                        </div>
                    </MediaQuery>
                    <div className="wrap-menu">
                        <motion.button
                            className="nav-menu-button"
                            onClick={() => set(!isOpen)}
                        >
                            <motion.div
                                className="img-wrap"
                                variants={{
                                open: { rotate: 180 },
                                closed: { rotate: 0 }
                                }}
                                transition={{ duration: 0.2 }}
                                style={{ originY: 0.55 }}
                            >
                                <svg width="35" height="35" viewBox="0 0 20 20">
                                    <path d="M0 7 L 20 7 L 10 16" />
                                </svg>
                            </motion.div>
                        </motion.button>
                        <motion.div
                            className="nav-menu-box"
                            style={{
                                top: isOpen ? "100px" : "-400px",
                                transition: "0.5s"
                            }}
                        >
                            <div className="wrap-box-a">
                                <div>
                                    <a href="" className="nav-box-a">Главная</a>
                                </div>
                                <div>
                                    <a href="" className="nav-box-a">Технология</a>
                                </div>
                                <div>
                                    <a href="" className="nav-box-a">График полётов</a>
                                </div>
                                <div>
                                    <a href="" className="nav-box-a">Гарантии</a>
                                </div>
                                <div>
                                    <a href="" className="nav-box-a">О компании</a>
                                </div>
                                <div>
                                    <a href="" className="nav-box-a">Контакты</a>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                </motion.nav>
            </MediaQuery>
        </>
    )
}

const MainFrame = () => {
    return (
        <>
            <MediaQuery minWidth={1399}>
                <div className="wrap">
                    <div className="title-wrap">
                        <div className="mars-title">
                            <h1 className="mars-text-high">ПУТЕШЕСТВИЕ</h1>
                            <p className="mars-text">на красную планету</p>
                        </div>
                        <button className="mars-button">
                            <img src={marsButtonBox} alt="marsButtonBox" />
                            <p className="mars-button-text">Начать Путешествие</p>
                        </button>
                    </div>
                    <div className="middle-content">
                        <img src={planet} alt="planet" className="planet" />
                        <img src={pointMars} alt="point to mars" className="point-to-mars" />
                    </div>
                    <InfoBoxes />
                </div>
            </MediaQuery>
            <MediaQuery maxWidth={1399}>
                <div className="wrap">
                    <div className="title-wrap">
                        <div className="mars-title">
                            <h1 className="mars-text-high">ПУТЕШЕСТВИЕ</h1>
                            <p className="mars-text">на красную планету</p>
                        </div>
                        <button className="mars-button">
                            <img src={marsButtonBox} alt="marsButtonBox" />
                            <p className="mars-button-text">Начать Путешествие</p>
                        </button>
                    </div>
                    <div className="info-seg-wrap">
                        <InfoBoxes />
                    </div>
                </div>
            </MediaQuery>
        </>
    )
}

const InfoBoxes = () => {
    return (
        <div className="info-boxes-container">
            <div className="info-box-tl">
                <div className="info-box-a-tl">
                    <p className="info-box-text">мы</p>
                    <h1 className="info-box-text-high">1</h1>
                    <p className="info-box-text">на рынке</p>
                </div>
            </div>
            <div className="info-box-tr">
                <div className="info-box-a-tr">
                    <p className="info-box-text">гарантируем</p>
                    <h1 className="info-box-text-high">50%</h1>{/* фетч даты */}
                    <p className="info-box-text">безопасность</p>
                </div>
            </div>
            <div className="info-box-br">
                <div className="info-box-a-br">
                    <p className="info-box-text">календарик за</p>
                    <h1 className="info-box-text-high">2001<span>г.</span></h1>{/* фетч даты */}
                    <p className="info-box-text">в подарок</p>
                </div>
            </div>
            <div className="info-box-bl">
                <div className="info-box-a-bl">
                    <p className="info-box-text">путешествие</p>
                    <h1 className="info-box-text-high">597</h1>{/* фетч даты */}
                    <p className="info-box-text">дней</p>
                </div>
            </div>
        </div>
    )
}