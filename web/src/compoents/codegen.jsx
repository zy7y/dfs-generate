import { Tabs, message } from "antd";

import PythonEditor from "./python";
import { TableOutlined } from "@ant-design/icons";
import { useEffect, useState } from "react";
import useWindowSize from "../hooks/useWindowSize";
import { host } from "../conf";

// 单张表
const TableItem = ({ codes }) => {
  return (
    <Tabs
      defaultActiveKey="1"
      items={codes?.map((item) => {
        return {
          label: item.name,
          key: item.key,
          children: <PythonEditor code={item.code} />,
        };
      })}
    />
  );
};

const CodeGenerate = ({ tables, mode }) => {
  const [selectTable, setSelectTable] = useState(tables[0]);
  const [generateCodes, setGenerateCodes] = useState([]);

  const { windowWidth, windowHeight } = useWindowSize();

  const changeTableGetCode = async () => {
    // await
    const res = await fetch(
      `${host}/codegen?tableName=${selectTable}&mode=${mode}`
    );
    const resData = await res.json();
    console.log(resData);
    if (resData?.code == 40000) {
      message.error(resData.msg);
    } else {
      setGenerateCodes(resData.data);
    }
  };
  useEffect(() => {
    changeTableGetCode();
  }, [selectTable]);

  return (
    <Tabs
      defaultActiveKey={selectTable}
      tabPosition="left"
      style={{ height: `${windowHeight}px` }}
      onChange={(value) => setSelectTable(value)}
      // tabBarStyle={{ width: 200, overflowX: "auto" }}
      // indicatorSize={(v) => v - 200}
      items={tables?.map((item) => {
        return {
          label: item,
          icon: <TableOutlined />,
          key: item,
          children: <TableItem codes={generateCodes} />,
        };
      })}
    />
  );
};
export default CodeGenerate;
