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
        value: function createScrollspyToC() {}

        // prepares the elements where user will enter information

    }, {
        key: "createConfigOptions",
        value: function createConfigOptions() {}
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
                    return "Selected PDB2PQR";
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