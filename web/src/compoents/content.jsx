import {
  Modal,
  Table,
  Form,
  Drawer,
  Button,
  Input,
  InputNumber,
  message,
  Affix
} from 'antd'
import { useEffect, useState } from 'react'
import {
  CodepenOutlined,
  SettingOutlined,
  RedditOutlined
} from '@ant-design/icons'
import CodeGenerate from '../compoents/codegen'
import { host } from '../conf'

const changDBFormRules = [{ required: true, message: '该项必须填写' }]

// 修改配置组件
const ChangeDB = ({ onDbFinsh, initialValues }) => {
  return (
    <Form
      onFinish={(values) => onDbFinsh(values)}
      initialValues={initialValues}
    >
      <Form.Item
        name="host"
        rules={changDBFormRules}
        initialValue={'127.0.0.1'}
      >
        <Input placeholder="主机地址如：127.0.0.1"></Input>
      </Form.Item>
      <Form.Item name="user" rules={changDBFormRules}>
        <Input placeholder="账号如：root"></Input>
      </Form.Item>
      <Form.Item
        name="password"
        rules={changDBFormRules}
        initialValue={'123456'}
      >
        <Input.Password placeholder="密码如：123456"></Input.Password>
      </Form.Item>
      <Form.Item name="db" rules={changDBFormRules}>
        <Input placeholder="数据库名称如：mini-rbac"></Input>
      </Form.Item>
      <Form.Item name="port" label="端口号">
        <InputNumber placeholder="如：3306"></InputNumber>
      </Form.Item>
      <Form.Item>
        <Button htmlType="submit" block type="primary">
          确认修改
        </Button>
      </Form.Item>
    </Form>
  )
}

const columns = [
  {
    title: '表名',
    dataIndex: 'tableName'
  },
  {
    title: '描述',
    dataIndex: 'tableComment'
  }
]

const DFSContent = () => {
  const [tableData, setTableData] = useState([])
  const [selectTable, setSelectTable] = useState([])
  const [initialValues, setInitialValues] = useState({})

  const getTables = async (data = '') => {
    const res = await fetch(`${host}/tables?tableName=${data}`)
    const resData = await res.json()
    if (resData.code === 40000) {
      message.error(resData.msg)
      return
    }
    setTableData(resData.data)
  }

  // 获取数据链接
  const getConnect = async () => {
    const res = await fetch(`${host}/con`)
    const resData = await res.json()
    if (resData.code === 40000) {
      message.info('welcome to use dfs-generate')
      setModalOpen(true)
      return
    } else {
      setInitialValues(resData.data)
      await getTables()
    }
  }
  useEffect(() => {
    getConnect()
  }, [])

  // 搜索
  const onSearch = async (values) => {
    await getTables(values?.tableName)
  }

  // 选中表
  const rowSelection = {
    onChange: (selectedRowKeys, selectedRows) => {
      console.log(
        `selectedRowKeys: ${selectedRowKeys}`,
        'selectedRows: ',
        selectedRows
      )
      setSelectTable(selectedRows.map((e) => e.tableName))
    }
  }

  // 修改连接

  const [modalOpen, setModalOpen] = useState(false)

  const onDbFinsh = async (values) => {
    const res = await fetch(`${host}/conf`, {
      method: 'post',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(values)
    })
    const resBody = await res.json()
    if (resBody.code === 40000) {
      message.error(resBody.msg)
    } else {
      message.success(resBody.msg)
      setModalOpen(false)
      setInitialValues(values)
      await getTables()
    }
  }

  // 生成代码
  const [openDrawer, setOpenDrawer] = useState(false)
  const [mode, setMode] = useState('sqlmodel')

  return (
    <div>
      <Affix offsetTop={10}>
        <Form layout="inline" onFinish={onSearch}>
          <Form.Item name="tableName" initialValue={''}>
            <Input placeholder="搜索表名" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit">
              搜索
            </Button>
          </Form.Item>
          <Form.Item>
            <Button
              onClick={() => {
                setOpenDrawer(true)
                setMode('sqlmodel')
              }}
              disabled={!selectTable.length}
            >
              <RedditOutlined />
              SQLModel
            </Button>
          </Form.Item>
          <Form.Item>
            <Button
              onClick={() => {
                setOpenDrawer(true)
                setMode('tortoise')
              }}
              disabled={!selectTable.length}
            >
              <CodepenOutlined />
              Tortoise ORM
            </Button>
          </Form.Item>
          <Form.Item>
            <Button type="dashed" onClick={() => setModalOpen(true)}>
              <SettingOutlined />
              修改连接
            </Button>
          </Form.Item>
        </Form>
      </Affix>

      <Table
        style={{ marginTop: '20px' }}
        rowSelection={{
          type: 'checkbox',
          ...rowSelection
        }}
        pagination={false}
        dataSource={tableData}
        columns={columns}
      />
      <Modal
        open={modalOpen}
        width={300}
        footer={null}
        title="DB配置"
        destroyOnClose={true}
        onCancel={() => setModalOpen(false)}
      >
        <ChangeDB onDbFinsh={onDbFinsh} initialValues={initialValues} />
      </Modal>

      <Drawer
        styles={{
          body: { padding: '0px' }
        }}
        width="75%"
        placement="right"
        closable={false}
        onClose={() => setOpenDrawer(false)}
        open={openDrawer}
        destroyOnClose={true}
        keyboard={false}
      >
        <CodeGenerate tables={selectTable} mode={mode} />
      </Drawer>
    </div>
  )
}

export default DFSContent
