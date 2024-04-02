import "./App.css";
import { GithubOutlined } from "@ant-design/icons";
import Logo from "./assets/logo.png";

import DFSContent from "./compoents/content";

const visitGithub = () => {
  window.open("https://github.com/zy7y/dfs-generate");
};

function App() {
  return (
    <div>
      <div className="project">
        <img src={Logo} className="logo"></img>
        <div className="left" onClick={visitGithub}>
          <GithubOutlined />
        </div>
      </div>
      <div id="app">
        <DFSContent />
      </div>
    </div>
  );
}

export default App;
