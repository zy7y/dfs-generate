import AceEditor from "react-ace";
import copy from "copy-to-clipboard";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import { message } from "antd";
import { CopyOutlined } from "@ant-design/icons";
import "./index.css";
import useWindowSize from "../hooks/useWindowSize";

const PythonEditor = ({ code }) => {
  const { windowWidth, windowHeight } = useWindowSize();
  console.log(windowHeight, windowWidth);

  const handleCopyClick = () => {
    copy(code);
    message.success("已复制到剪贴板");
  };

  return (
    <div className="editor-wrapper">
      <div className="copy-icon">
        <CopyOutlined onClick={handleCopyClick} />
      </div>
      <AceEditor
        mode="python"
        theme="monokai"
        name="python-editor"
        fontSize={14}
        showPrintMargin={true}
        showGutter={true}
        highlightActiveLine={true}
        value={code}
        width="100%"
        height={`${windowHeight - 46 - 24 - 16}px`}
        readOnly={true}
      />
    </div>
  );
};

export default PythonEditor;
