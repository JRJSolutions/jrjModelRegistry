import { CheckOutlined, CloseOutlined, SearchOutlined } from "@ant-design/icons";
import { Button, DatePicker, Input, Select } from "antd";
import moment from "moment";
import { apiCallWithToken } from "./utils/apis";

const { TextArea } = Input;

export const modelsColumns = ({
    //
    modelsStateSet,
    modelsState,
}) => {
    return [
        {
            title: "_id",
            dataIndex: "_id",
            key: "_id",
            align: "center",
            width: 1,
            padding: 0,
            sorter: {
                multiple: 1,
                compare: () => { },
            },
            render: (text) => <span style={{ fontSize: "9px" }}>{text}</span>,
        },
        {
            title: "CreatedAt",
            dataIndex: "createdAt",
            key: "createdAt",
            align: "center",
            width: 1,
            padding: 0,
            sorter: {
                multiple: 1,
                compare: () => { },
            },
            render: (createdAt) => (
                <p
                    style={{
                        fontSize: 9,
                        textAlign: "center",
                        margin: 0,
                    }}>
                    {moment(createdAt).format("YYYY-MM-DD HH:mm")}
                </p>
            ),
            filterDropdown: ({ confirm, clearFilters }) => (
                <div style={{ padding: 8 }}>
                    <DatePicker.RangePicker
                        showTime
                        style={{ display: "block", marginBottom: 8 }}
                        onChange={(dates, dateStrings) => {
                            modelsStateSet((draft) => {
                                if (dates) {
                                    draft.search.where.createdAt = {
                                        $gte: moment(dateStrings[0]),
                                        $lte: moment(dateStrings[1]),
                                    };
                                } else {
                                    delete draft.search.where.createdAt;
                                }
                            });
                            if (!modelsState?.needToUpdate) {
                                modelsStateSet((draft) => {
                                    draft.needToUpdate = true;
                                });
                            }
                        }}
                    />
                    <Button
                        onClick={() => {
                            clearFilters();
                            modelsStateSet((draft) => {
                                delete draft.search.where.start;
                            });
                            confirm();
                            if (!modelsState?.needToUpdate) {
                                modelsStateSet((draft) => {
                                    draft.needToUpdate = true;
                                });
                            }
                        }}
                        size="small"
                        style={{ width: "100%" }}>
                        Reset
                    </Button>
                </div>
            ),
        },
        {
            title: "UpdatedAt",
            dataIndex: "updatedAt",
            key: "updatedAt",
            align: "center",
            width: 1,
            padding: 0,
            sorter: {
                multiple: 1,
                compare: () => { },
            },
            render: (updatedAt) => (
                <p
                    style={{
                        fontSize: 9,
                        textAlign: "center",
                        margin: 0,
                    }}>
                    {moment(updatedAt).format("YYYY-MM-DD HH:mm")}
                </p>
            ),
            filterDropdown: ({ confirm, clearFilters }) => (
                <div style={{ padding: 8 }}>
                    <DatePicker.RangePicker
                        showTime
                        style={{ display: "block", marginBottom: 8 }}
                        onChange={(dates, dateStrings) => {
                            modelsStateSet((draft) => {
                                if (dates) {
                                    draft.search.where.updatedAt = {
                                        $gte: moment(dateStrings[0]),
                                        $lte: moment(dateStrings[1]),
                                    };
                                } else {
                                    delete draft.search.where.updatedAt;
                                }
                            });
                            if (!modelsState?.needToUpdate) {
                                modelsStateSet((draft) => {
                                    draft.needToUpdate = true;
                                });
                            }
                        }}
                    />
                    <Button
                        onClick={() => {
                            clearFilters();
                            modelsStateSet((draft) => {
                                delete draft.search.where.start;
                            });
                            confirm();
                            if (!modelsState?.needToUpdate) {
                                modelsStateSet((draft) => {
                                    draft.needToUpdate = true;
                                });
                            }
                        }}
                        size="small"
                        style={{ width: "100%" }}>
                        Reset
                    </Button>
                </div>
            ),
        },
        {
            title: "Model name",
            dataIndex: "modelName",
            key: "modelName",
            align: "center",
            width: 3,
            padding: 0,
            sorter: {
                multiple: 1,
                compare: () => { },
            },
            render: (text) => <span style={{ fontSize: "9px" }}>{text}</span>,
            filterIcon: (filtered) => <SearchOutlined />,
            filterDropdown: () => (
                <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
                    <Input
                        placeholder={`Search modelName`}
                        onChange={(event) => {
                            modelsStateSet((draft) => {
                                if (event.target.value) {
                                    draft.search.where.modelName = {
                                        $regex: event.target.value,
                                    };
                                } else {
                                    delete draft.search.where.modelName;
                                }
                            });

                            setTimeout(() => {
                                if (!modelsState?.needToUpdate) {
                                    modelsStateSet((draft) => {
                                        draft.needToUpdate = true;
                                    });
                                }
                            }, 500);
                        }}
                        style={{
                            marginBottom: 8,
                            display: "block",
                        }}
                    />
                </div>
            ),
        },
        {
            title: "Version",
            dataIndex: "version",
            key: "version",
            align: "center",
            width: 1,
            padding: 0,
            sorter: {
                multiple: 1,
                compare: () => { },
            },
            render: (text) => <span style={{ fontSize: "9px" }}>{text}</span>,
            filterIcon: (filtered) => <SearchOutlined />,
            filterDropdown: () => (
                <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
                    <Input
                        placeholder={`Search version`}
                        onChange={(event) => {
                            modelsStateSet((draft) => {
                                if (event.target.value) {
                                    draft.search.where.version = {
                                        $regex: event.target.value,
                                    };
                                } else {
                                    delete draft.search.where.version;
                                }
                            });

                            setTimeout(() => {
                                if (!modelsState?.needToUpdate) {
                                    modelsStateSet((draft) => {
                                        draft.needToUpdate = true;
                                    });
                                }
                            }, 500);
                        }}
                        style={{
                            marginBottom: 8,
                            display: "block",
                        }}
                    />
                </div>
            ),
        },
        {
            title: "Ticker",
            dataIndex: "ticker",
            key: "ticker",
            align: "center",
            width: 1,
            padding: 0,
            sorter: {
                multiple: 1,
                compare: () => { },
            },
            render: (text) => <span style={{ fontSize: "9px" }}>{text}</span>,
            filterIcon: (filtered) => <SearchOutlined />,
            filterDropdown: () => (
                <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
                    <Input
                        placeholder={`Search ticker`}
                        onChange={(event) => {
                            modelsStateSet((draft) => {
                                if (event.target.value) {
                                    draft.search.where.ticker = {
                                        $regex: event.target.value,
                                    };
                                } else {
                                    delete draft.search.where.ticker;
                                }
                            });

                            setTimeout(() => {
                                if (!modelsState?.needToUpdate) {
                                    modelsStateSet((draft) => {
                                        draft.needToUpdate = true;
                                    });
                                }
                            }, 500);
                        }}
                        style={{
                            marginBottom: 8,
                            display: "block",
                        }}
                    />
                </div>
            ),
        },
        {
            title: "Side",
            dataIndex: "side",
            key: "side",
            align: "center",
            width: 1,
            padding: 0,
            sorter: {
                multiple: 1,
                compare: () => { },
            },
            render: (text) => <span style={{ fontSize: "9px" }}>{text}</span>,
            filterIcon: (filtered) => <SearchOutlined />,
            filterDropdown: () => (
                <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
                    <Input
                        placeholder={`Search side`}
                        onChange={(event) => {
                            modelsStateSet((draft) => {
                                if (event.target.value) {
                                    draft.search.where.side = {
                                        $regex: event.target.value,
                                    };
                                } else {
                                    delete draft.search.where.side;
                                }
                            });

                            setTimeout(() => {
                                if (!modelsState?.needToUpdate) {
                                    modelsStateSet((draft) => {
                                        draft.needToUpdate = true;
                                    });
                                }
                            }, 500);
                        }}
                        style={{
                            marginBottom: 8,
                            display: "block",
                        }}
                    />
                </div>
            ),
        },
        {
            title: "Score",
            dataIndex: "score",
            key: "score",
            align: "center",
            width: 1,
            padding: 0,
            sorter: {
                multiple: 1,
                compare: () => { },
            },
            render: (text) => <span style={{ fontSize: "9px" }}>{Number(parseFloat(text || 0).toFixed(3))}</span>,
            filterIcon: (filtered) => <SearchOutlined />,
            filterDropdown: () => (
                <div style={{ padding: 8 }} onKeyDown={(e) => e.stopPropagation()}>
                    <Input
                        placeholder={`Search score`}
                        onChange={(event) => {
                            modelsStateSet((draft) => {
                                if (event.target.value) {
                                    draft.search.where.score = {
                                        $regex: event.target.value,
                                    };
                                } else {
                                    delete draft.search.where.score;
                                }
                            });

                            setTimeout(() => {
                                if (!modelsState?.needToUpdate) {
                                    modelsStateSet((draft) => {
                                        draft.needToUpdate = true;
                                    });
                                }
                            }, 500);
                        }}
                        style={{
                            marginBottom: 8,
                            display: "block",
                        }}
                    />
                </div>
            ),
        },
        {
            title: "Is Real",
            key: "random_data",
            align: "center",
            width: 1,
            padding: 0,
            render: (row) => (!row?.random_data ? <CheckOutlined /> : <CloseOutlined />),
            filterDropdown: () => (
                <div style={{ padding: 8 }}>
                    <Select
                        style={{ width: 120 }}
                        placeholder="Select"
                        allowClear
                        onChange={(value) => {
                            modelsStateSet((draft) => {
                                if (value === undefined) {
                                    delete draft.search.where.random_data;
                                } else {
                                    draft.search.where.random_data = value === "true";
                                }
                                draft.needToUpdate = true;
                            });
                        }}
                        options={[
                            { label: "✓", value: "false" },
                            { label: "✗", value: "true" },
                        ]}
                    />
                </div>
            ),
        },

        {
            title: "Model Type",
            dataIndex: "modelType",
            key: "modelType",
            align: "center",
            width: 2,
            padding: 0,
            render: (text) => <span style={{ fontSize: "9px" }}>{text || "-"}</span>,
            filterDropdown: ({ setSelectedKeys, selectedKeys, confirm }) => (
                <div style={{ padding: 8 }}>
                    <Select
                        style={{ width: 120 }}
                        placeholder="Select type"
                        value={selectedKeys[0]}
                        onChange={(value) => {
                            setSelectedKeys(value ? [value] : []);
                            confirm();
                        }}
                        allowClear>
                        <Select.Option value="model">model</Select.Option>
                        <Select.Option value="data">data</Select.Option>
                        <Select.Option value="empty">empty</Select.Option>
                    </Select>
                </div>
            ),
            onFilter: (value, record) => {
                if (value === "empty") return !record.modelType;
                return record.modelType === value;
            },
        },
        {
            title: "Model Size (GB)",
            dataIndex: "modelSizeBytes",
            key: "modelSizeBytes",
            align: "center",
            width: 2,
            padding: 0,
            render: (bytes) => {
                const gb = bytes ? (bytes / 1024 ** 3).toFixed(2) : "-";
                return <span style={{ fontSize: "9px" }}>{gb}</span>;
            },
        },
        {
            title: "Zip Size (GB)",
            dataIndex: "zippedModelSizeBytes",
            key: "zippedModelSizeBytes",
            align: "center",
            width: 2,
            padding: 0,
            render: (bytes) => {
                const gb = bytes ? (bytes / 1024 ** 3).toFixed(2) : "-";
                return <span style={{ fontSize: "9px" }}>{gb}</span>;
            },
        },
        {
            title: "Action",
            // key: "action",
            align: "center",
            width: modelsState?.textboxTestId ? 10 : 1,
            padding: 0,
            render: (row) => {
                // console.log(row);
                return (
                    <div style={{ display: "flex", justifyContent: "center", gap: "8px", flexDirection: "column" }}>
                        <Button
                            danger
                            size="small"
                            onClick={async () => {
                                try {
                                    const result = await apiCallWithToken({
                                        url: "jrjModelRegistry/deleteModelById",
                                        options: {
                                            method: "POST",
                                            headers: {},
                                            body: JSON.stringify({
                                                id: row._id,
                                            }),
                                        },
                                    });
                                    if (!result?.deleted) {
                                        throw new Error(result);
                                    }
                                    setTimeout(() => {
                                        if (!modelsState?.needToUpdate) {
                                            modelsStateSet((draft) => {
                                                draft.needToUpdate = true;
                                            });
                                        }
                                    }, 500);
                                } catch (error) {
                                    console.error("Error deleting:", error);
                                    alert("Error during deleting.");
                                }
                            }}>
                            Delete
                        </Button>
                        {
                            row?.sampleData && !modelsState?.textboxTestId
                            && <Button
                                primary
                                size="small"
                                onClick={async () => {

                                    modelsStateSet((draft) => {
                                        draft.textboxTestId = row._id;
                                        draft.textboxSampleData = JSON.stringify(row?.sampleData, 0, 4)
                                    });
                                    return
                                }}>
                                Test
                            </Button>
                        }
                        {
                            modelsState?.textboxTestId == row._id

                            && <>
                                <TextArea
                                    //
                                    value={modelsState?.textboxSampleData || ""}
                                    onChange={(event) => {
                                        modelsStateSet((draft) => {
                                            draft.textboxSampleData = event.target.value;
                                        });
                                    }}
                                    rows={6} />
                                <Button
                                    primary
                                    size="small"
                                    onClick={async () => {
                                        try {
                                            const result = await apiCallWithToken({
                                                url: "jrjModelRegistry/selectModelAndPredict",
                                                options: {
                                                    method: "POST",
                                                    headers: {},
                                                    body: JSON.stringify({
                                                        "where": {
                                                            "modelName": row.modelName,
                                                            "version": row.version
                                                        },
                                                        "data": JSON.parse(modelsState.textboxSampleData)
                                                    }),
                                                },
                                            });
                                            alert(`Result for modelName: ${row.modelName} and version ${row.version} is \n${JSON.stringify(result, 0, 4)}`)
                                            setTimeout(() => {
                                                if (!modelsState?.needToUpdate) {
                                                    modelsStateSet((draft) => {
                                                        draft.needToUpdate = true;
                                                    });
                                                }
                                            }, 500);
                                        } catch (error) {
                                            console.error("Error deleting:", error);
                                            alert("Error during deleting.");
                                        }

                                        modelsStateSet((draft) => {
                                            draft.textboxTestId = null;
                                            draft.textboxSampleData = null
                                        });
                                        return

                                    }}>
                                    run
                                </Button>
                            </>

                        }
                    </div>
                );
            },
        },
    ];
};
