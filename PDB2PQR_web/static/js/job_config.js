'use strict';

// class SubmitButton extends React.Component{}
// class FormWindowHeader extends React.Component{}

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

function Button(props) {
    return React.createElement(
        "button",
        { type: "button", className: props.buttonType, onClick: props.onClick },
        props.value
    );
}

var JobLanding = function (_React$Component) {
    _inherits(JobLanding, _React$Component);

    function JobLanding() {
        _classCallCheck(this, JobLanding);

        return _possibleConstructorReturn(this, (JobLanding.__proto__ || Object.getPrototypeOf(JobLanding)).apply(this, arguments));
    }

    _createClass(JobLanding, [{
        key: "createButton",
        value: function createButton(txt, additional_classNames) {
            var _this2 = this;

            return React.createElement(Button, {
                value: txt,
                buttonType: additional_classNames,
                onClick: function onClick() {
                    return _this2.props.onClick(txt);
                }
            });
        }
    }, {
        key: "createWindow",
        value: function createWindow(option_list) {
            var view = [];

            for (var i = 0; i < option_list.length; i++) {
                view.push(this.createButton(option_list[i], "btn btn-primary mx-1"));
            }

            return view;
        }
    }, {
        key: "render",
        value: function render() {
            return React.createElement(
                "section",
                { className: "jumbotron text-center" },
                React.createElement(
                    "div",
                    { className: "container" },
                    React.createElement(
                        "h1",
                        { className: "jumbotron-heading" },
                        "Welcome to the PDB2PQR Server"
                    ),
                    React.createElement(
                        "p",
                        { className: "lead text-muted" },
                        "This server enables a user to convert PDB files into PQR files. PQR files are PDB files where the occupancy and B-factor columns have been replaced by per-atom charge and radius."
                    ),
                    React.createElement(
                        "p",
                        null,
                        this.createWindow(this.props.job_list)
                    )
                )
            );
        }
    }]);

    return JobLanding;
}(React.Component);

var ConfigPDB2PQR = function (_React$Component2) {
    _inherits(ConfigPDB2PQR, _React$Component2);

    function ConfigPDB2PQR() {
        _classCallCheck(this, ConfigPDB2PQR);

        return _possibleConstructorReturn(this, (ConfigPDB2PQR.__proto__ || Object.getPrototypeOf(ConfigPDB2PQR)).apply(this, arguments));
    }

    _createClass(ConfigPDB2PQR, [{
        key: "createScrollspyToC",

        // prepares the list-group for the parts of configuration
        value: function createScrollspyToC(scrollspy_name, names_map) {
            var all_headers = [];
            names_map.forEach(function (value, key, map) {
                all_headers.push(React.createElement(
                    "a",
                    { className: "list-group-iterm list-group-item-action", href: '#'.concat(key) },
                    value
                ));
            });
            return React.createElement(
                "div",
                { id: scrollspy_name, className: "list-group" },
                all_headers
            );
        }

        // prepares the elements where user will enter information

    }, {
        key: "createConfigOptions",
        value: function createConfigOptions(scrollspy_name) {

            return React.createElement("div", { "data-spy": "scroll", "data-target": '#'.concat(scrollspy_name), className: "list-group" });
        }
    }, {
        key: "render",
        value: function render() {

            return React.createElement(
                "form",
                null,
                this.createScrollspyToC(this.props.scrollspy_name, this.props.config_headers),
                this.createConfigOptions(this.props.scrollspy_name, this.props.config_headers)
            );
        }
    }]);

    return ConfigPDB2PQR;
}(React.Component);

var Configuration = function (_React$Component3) {
    _inherits(Configuration, _React$Component3);

    function Configuration(props) {
        _classCallCheck(this, Configuration);

        var _this4 = _possibleConstructorReturn(this, (Configuration.__proto__ || Object.getPrototypeOf(Configuration)).call(this, props));

        _this4.selectJobClick = _this4.selectJobClick.bind(_this4);
        _this4.state = {
            job_type: null,

            // Maintains state for PDB2PQR configuration in case user hops back and forth
            pdb2pqr_settings: {
                pdb_id: null,
                ff: null,
                output_scheme: null
            },

            // Maintains state for APBS for same purpose as pdb2pqr_settings
            apbs_settings: {}
        };
        return _this4;
    }

    // onClick handler for user selecting a job. Is passed into child componenets


    _createClass(Configuration, [{
        key: "selectJobClick",
        value: function selectJobClick(selected_job) {
            this.setState({
                job_type: selected_job
            });
        }

        // 

    }, {
        key: "handleConfigClick",
        value: function handleConfigClick(selected_job, option, selection) {
            this.setState({
                selected_job: {
                    option: selection
                }
            });
        }
    }, {
        key: "render",
        value: function render() {
            var _this5 = this;

            // Renders landing page, with choice to do PDB2PQR or APBS
            if (this.state.job_type == null) {
                var job_options = ["PDB2PQR", "APBS"];
                document.body.id = 'body';
                // let blah = <JobLanding onClick={j => this.selectJobClick(j)}/>
                return React.createElement(JobLanding, {
                    job_list: job_options,
                    onClick: function onClick(j) {
                        return _this5.selectJobClick(j);
                    }
                });
            }

            // Renders configuration elements to set up an PDB2PQR job
            else if (this.state.job_type == "PDB2PQR") {
                    var pdb2pqr_scrollspy = "pdb2pqr_config";
                    var pdb2pqr_headers = new Map();
                    pdb2pqr_headers.set("which_pdb", "PDB ID Entry");
                    pdb2pqr_headers.set("which_ff", "Forcefield");
                    pdb2pqr_headers.set("which_output", "Output Naming Scheme");
                    pdb2pqr_headers.set("which_options", "Output Naming Scheme");
                    pdb2pqr_headers.set("which_pka", "pKa Settings (optional)");
                    pdb2pqr_headers.set("submission", "Start Job");

                    // document.body.data\-spy = 'body';
                    $('#body').attr('data-spy', 'body');

                    return (
                        // <ConfigPDB2PQR
                        //     scrollspy_name={pdb2pqr_scrollspy}
                        //     config_headers={pdb2pqr_headers}
                        // />
                        React.createElement(
                            "div",
                            { className: "row position-relative my-scrollspy-overflow-y" },
                            React.createElement(
                                "div",
                                { id: "list-example", className: "list-group col-2 position-fixed text-center" },
                                React.createElement(
                                    "a",
                                    { "class": "list-group-item list-group-item-action active", href: "#list-item-1" },
                                    "Item 1"
                                ),
                                React.createElement(
                                    "a",
                                    { "class": "list-group-item list-group-item-action", href: "#list-item-2" },
                                    "Item 2"
                                ),
                                React.createElement(
                                    "a",
                                    { "class": "list-group-item list-group-item-action", href: "#list-item-3" },
                                    "Item 3"
                                ),
                                React.createElement(
                                    "a",
                                    { "class": "list-group-item list-group-item-action", href: "#list-item-4" },
                                    "Item 4"
                                )
                            ),
                            React.createElement(
                                "div",
                                { "data-spy": "scroll", "data-target": "#list-example", "data-offset": "0", className: "col-8 " },
                                React.createElement(
                                    "h4",
                                    { id: "list-item-1" },
                                    "Item 1"
                                ),
                                React.createElement(
                                    "p",
                                    null,
                                    "Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore."
                                ),
                                React.createElement(
                                    "h4",
                                    { id: "list-item-2" },
                                    "Item 2"
                                ),
                                React.createElement(
                                    "p",
                                    null,
                                    "Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore."
                                ),
                                React.createElement(
                                    "h4",
                                    { id: "list-item-3" },
                                    "Item 3"
                                ),
                                React.createElement(
                                    "p",
                                    null,
                                    "Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore."
                                ),
                                React.createElement(
                                    "h4",
                                    { id: "list-item-4" },
                                    "Item 4"
                                ),
                                React.createElement(
                                    "p",
                                    null,
                                    "Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore. Ex consequat commodo adipisicing exercitation aute excepteur occaecat ullamco duis aliqua id magna ullamco eu. Do aute ipsum ipsum ullamco cillum consectetur ut et aute consectetur labore. Fugiat laborum incididunt tempor eu consequat enim dolore proident. Qui laborum do non excepteur nulla magna eiusmod consectetur in. Aliqua et aliqua officia quis et incididunt voluptate non anim reprehenderit adipisicing dolore ut consequat deserunt mollit dolore. Aliquip nulla enim veniam non fugiat id cupidatat nulla elit cupidatat commodo velit ut eiusmod cupidatat elit dolore."
                                )
                            )
                        )
                    );
                }

                // Renders configuration elements to set up an APBS job
                else if (this.state.job_type == "APBS") {
                        return "Selected APBS";
                    }

                    // This should be unreachable since the state is only changed via a button press
                    else {
                            return "job_type is invalid";
                        }
        }
    }]);

    return Configuration;
}(React.Component);

// let domContainer = );


ReactDOM.render(React.createElement(Configuration, null), document.getElementById('choose_job'));