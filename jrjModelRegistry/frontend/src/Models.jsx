import { useSearchParams } from "react-router";
import _ from "lodash";
import { useImmer } from "use-immer";
import { FeaturesTableCss } from "./FeaturesTableCss";

import { useAsync } from "react-async-hook";
import { apiCallWithToken } from "./utils/apis";
import { Alert, Button, ConfigProvider, Flex, Pagination, Table, Typography, notification } from "antd";
import { useState } from "react";
import { getConfigUtils } from "./configUtils";
import { modelsColumns } from "./modelsColumns";
import ReactJson from 'react-json-view'

const { Text } = Typography;
//
export default function Models({ mainState, setMainState, projectSlug }) {
    const [loading, setLoading] = useState(false);
    const [api, contextHolder] = notification.useNotification();
    const [searchParams] = useSearchParams();

    const [modelsState, modelsStateSet] = useImmer({
        search: {
            orderBy: [
                {
                    _id: "desc",
                },
            ],
            where: {},
            select: {
                sample_raw_m1: 0,
                sample_raw_h1: 0,
                sample_raw_d1: 0,
                excluded: 0,
                transform_sample_result: 0,
            },
            include: {},
            pagination: {
                page: 1,
                size: 10,
            },
        },
        count: 0,
        errorMessage: "",
        successMessage: "",
        needToUpdate: true,
        data: [],
    });

    useAsync(async () => {
        if (!modelsState.needToUpdate) {
            return;
        }
        const result = await apiCallWithToken({
            url: "jrjModelRegistry/searchModelsCommon",
            options: {
                method: "POST",
                headers: {},
                body: JSON.stringify({
                    search: modelsState.search,
                }),
            },
        });
        modelsStateSet((draft) => {
            draft.needToUpdate = false;
            draft.data = result?.data || [];
            draft.count = result?.count || 0;
        });
    }, [modelsState.needToUpdate]);

    function onChangeTable(pagination, filters, sorter, extra) {
        if (_.isArray(sorter)) {
            const order = sorter.map((item) => {
                const result = {};
                result[item.columnKey] = item.order == "ascend" ? "asc" : "desc";

                return result;
            });
            modelsStateSet((draft) => {
                draft.search.orderBy = order;
                draft.needToUpdate = true;
            });
        } else if (sorter && sorter.order) {
            modelsStateSet((draft) => {
                const result = {};
                result[sorter.columnKey] = sorter.order == "ascend" ? "asc" : "desc";

                draft.search.orderBy = [result];
                draft.needToUpdate = true;
            });
        } else if (sorter) {
            modelsStateSet((draft) => {
                draft.search.orderBy = [
                    {
                        _id: "desc",
                    },
                ];
                draft.needToUpdate = true;
            });
        }
    }

    return (
        <div className="dashNexBackgroundFooterPageBackground">
            <FeaturesTableCss />
            {contextHolder}
            <Flex gap="middle" vertical className="FeaturesTable">
                <Flex justify="center">
                    <Text
                        style={{
                            ...getConfigUtils({ key: "tableName" }),
                        }}>
                        <b>Models</b>
                    </Text>
                </Flex>

                {modelsState.errorMessage && (
                    <Flex justify="center">
                        <Alert message={modelsState.errorMessage} type="error" />
                    </Flex>
                )}
                {modelsState.successMessage && (
                    <Flex justify="center">
                        <Alert message={modelsState.successMessage} type="info" />
                    </Flex>
                )}

                <ConfigProvider
                    theme={{
                        components: {
                            Table: {
                                cellPaddingBlockSM: 0,
                                cellPaddingInlineSM: 0,
                            },
                        },
                    }}>
                    <Flex justify="left">
                        <Pagination
                            total={modelsState.count}
                            showSizeChanger
                            showQuickJumper
                            showTotal={(total) => `${total} rows`}
                            onChange={(page, size) => {
                                modelsStateSet((draft) => {
                                    draft.search.pagination.page = page;
                                    draft.search.pagination.size = size;
                                    draft.needToUpdate = true;
                                });
                            }}
                            current={modelsState.search.pagination.page}
                        />
                        <Button
                            type="primary"
                            style={{
                                marginLeft: 20,
                                backgroundColor: " #20665a",
                                color: " #F9F4EA",
                            }}
                            onClick={async () => {
                                modelsStateSet((draft) => {
                                    draft.needToUpdate = true;
                                });
                            }}>
                            Refresh
                        </Button>
                    </Flex>
                    <Table
                        //
                        size="small"
                        dataSource={modelsState.data?.map((record) => ({
                            ...record,
                            key: record._id,
                        }))}
                        loading={modelsState.needToUpdate}
                        pagination={false}
                        scroll={{ x: 1000 }}
                        sticky={{ offsetHeader: 1 }}
                        onChange={onChangeTable}
                        expandable={{
                            rowExpandable: (record) => !!record._id,
                            columnWidth: 1,
                            expandedRowRender: (record) => {
                                return (
                                    <Flex
                                        style={{
                                            width: "100%",
                                        }}>
                                        <ReactJson src={record} collapsed={false} />
                                    </Flex>
                                );
                            },
                        }}
                        className="table-striped-rows"
                        columns={
                            modelsColumns({
                                modelsStateSet,
                                modelsState,
                            })
                            //
                        }
                        rowClassName={(record, index) => (index % 2 === 0 ? "even-row" : "odd-row")}
                    />
                </ConfigProvider>
            </Flex>
        </div>
    );
}
