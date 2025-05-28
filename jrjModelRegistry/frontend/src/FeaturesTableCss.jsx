import { getConfigUtils } from "./configUtils";

export const FeaturesTableCss = () => {
    return (
        <style
            jsx="true"
        //
        >{`
            .FeaturesTable table .ant-table-column-title{
                font-size: 8px !important;
            }
            .FeaturesTable table .ant-table-thead .ant-table-cell {
                background-color: #20665a !important;
                color: #f3f4f4 !important;
                text-align: center;
                font-weight: normal !important;
                font-size: 12px !important;
            }
            .FeaturesTable .ant-table-column-sorter-down.active,
            .ant-table-column-sorter-up.active {
                color: #5bc0de !important;
            }

            .FeaturesTable .ant-table-thead .anticon,
            .FeaturesTable .ant-table-thead .ant-table-selection-column {
                color: #fff;
            }
            .FeaturesTable .ant-table-column-sorters .ant-table-column-sorter-up,
            .FeaturesTable .ant-table-column-sorters .ant-table-column-sorter-down {
                color: #20665a;
            }

            .FeaturesTable .table-striped-rows th,
            .FeaturesTable .table-striped-rows td {
                border: 1px solid  #fff;
            }
            .FeaturesTable tr:nth-child(odd) {
                background: #f3f4f4;
                color:  #0d3b66;
            }
            .FeaturesTable tr:nth-child(even) {
                background: #fff;
                color:  #0d3b66;
            }

            .FeaturesTable td .ant-btn {
                padding: 3px;
            }
            .FeaturesTable .project-container {
                padding: 3px;
                border: 1px solid #332d2d";
                border-radius: 5px;
                transition: background-color 0.3s ease, border-color 0.3s ease;
            }
            .FeaturesTable .project-container:hover {
                background-color: f0f4f5;
                border-color: #7b95bb;
            }
            .FeaturesTable .project-container .project-link {
                font-size:12px;
                text-decoration: none;
                font-weight: bold;
                transition: color 0.3s ease
            }
            .FeaturesTable .project-container .project-link:hover {
                color: #605f4b;
            }
            .ant-card-head-title {
                color: #f3f4f4;
            }
            .ant-form-item-label label {
                color: #f3f4f4 !important;
            }
        `}</style>
    );
};
