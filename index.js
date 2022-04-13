/*
    This function publishes commands from the gxr2 alexa skill on an MQTT Broker.  It was derived from Amazon's Hello world example
    
    Lambda function.

    
*/

/**
 * App ID for the skill
 */
var APP_ID = undefined; //replace with "amzn1.echo-sdk-ams.app.[your-unique-value-here]";

/*****/
//Environment Configuration
var config = {};
config.IOT_BROKER_ENDPOINT      = "***broker endpoint goes here***".toLowerCase();
config.IOT_BROKER_REGION        = "***Region goes here***";
config.IOT_THING_NAME           = "***Thing name goes here***";
//Loading AWS SDK libraries
var AWS = require('aws-sdk');
AWS.config.region = config.IOT_BROKER_REGION;
//Initializing client for IoT
var iotData = new AWS.IotData({endpoint: config.IOT_BROKER_ENDPOINT});

var AlexaSkill = require('./AlexaSkill');

var gxr2 = function () {
    AlexaSkill.call(this, APP_ID);
};

// Extend AlexaSkill
gxr2.prototype = Object.create(AlexaSkill.prototype);
gxr2.prototype.constructor = gxr2;

gxr2.prototype.eventHandlers.onSessionStarted = function (sessionStartedRequest, session) {
    console.log("gxr2 onSessionStarted requestId: " + sessionStartedRequest.requestId
        + ", sessionId: " + session.sessionId);
    // any initialization logic goes here
};

gxr2.prototype.eventHandlers.onLaunch = function (launchRequest, session, response) {
    console.log("gxr2 onLaunch requestId: " + launchRequest.requestId + ", sessionId: " + session.sessionId);
    var speechOutput = "g x r two speaking.  what do you want.";
    var repromptText = "Please tell me what you want.";
    response.ask(speechOutput, repromptText);
};

gxr2.prototype.eventHandlers.onSessionEnded = function (sessionEndedRequest, session) {
    console.log("gxr2 onSessionEnded requestId: " + sessionEndedRequest.requestId
        + ", sessionId: " + session.sessionId);
    // any cleanup logic goes here
};

gxr2.prototype.intentHandlers = {
    // register custom intent handlers
    "setintent": function (intent, session, response) {
        console.log("FB started");
        /****/
        var repromptText = null;
        var sessionAttributes = {};
        var shouldEndSession = true;
        var speechOutput = "";
        var itype = "set";  //Intent Name
        var zone = intent.slots.zone.value; //Zone Name
        var device = intent.slots.device.value; // Device Name
        //Prepare the parameters of the update call
        var paramsUpdate = {
            topic:"niles/gxr2",
            payload: JSON.stringify(itype + ":" + zone + ":" + device),
            qos:0
        };
        iotData.publish(paramsUpdate, function(err, data) {
          if (err){
            //Handle the error here
            console.log("MQTT Error" + data);
          }
          else {
            speechOutput = (zone + "is set to " + device);
            console.log(data);
            response.tell(speechOutput);
            //callback(sessionAttributes,buildSpeechletResponse(intent.name, speechOutput, repromptText, shouldEndSession));
          }    
        });
    },
    
    "levelintent": function (intent, session, response) {
        console.log("FB started");
        /****/
        var repromptText = null;
        var sessionAttributes = {};
        var shouldEndSession = true;
        var speechOutput = "";
        var itype = "adjust";  //Intent Name
        var level = intent.slots.vollevel.value; // Volume level
        var zone = intent.slots.zone.value; // Device Name
        //Prepare the parameters of the update call
        var paramsUpdate = {
            topic:"niles/gxr2",
            payload: JSON.stringify(itype + ":" + zone + ":" + level),
            qos:0
        };
        iotData.publish(paramsUpdate, function(err, data) {
          if (err){
            //Handle the error here
            console.log("MQTT Error" + data);
          }
          else {
            speechOutput = ("Volume is turned to " + level + "on " + zone);
            console.log(data);
            response.tell(speechOutput);
            //callback(sessionAttributes,buildSpeechletResponse(intent.name, speechOutput, repromptText, shouldEndSession));
          }    
        });
    },
    
    "GoToIntent": function (intent, session, response) {
        console.log("FB started");
        /****/
        var repromptText = null;
        var sessionAttributes = {};
        var shouldEndSession = true;
        var speechOutput = "";
        var itype = "goto";  //Intent Name
        var prevnext = intent.slots.prevnext.value; // Volume level
        var device = intent.slots.device.value; // Device Name
        //Prepare the parameters of the update call
        var paramsUpdate = {
            topic:"niles/gxr2",
            payload: JSON.stringify(itype + ":" + prevnext + ":" + device),
            qos:0
        };
        iotData.publish(paramsUpdate, function(err, data) {
          if (err){
            //Handle the error here
            console.log("MQTT Error" + data);
          }
          else {
            speechOutput = (prevnext + "song is selected on " + device);
            console.log(data);
            response.tell(speechOutput);
            //callback(sessionAttributes,buildSpeechletResponse(intent.name, speechOutput, repromptText, shouldEndSession));
          }    
        });
    },
    
    "AMAZON.HelpIntent": function (intent, session, response) {
        response.ask("You can ask me to set a zone to a specific device.");
    }
};

// Create the handler that responds to the Alexa Request.
exports.handler = function (event, context) {
    // Create an instance of the gxr2 skill.
    var gxr2instance = new gxr2();
    gxr2instance.execute(event, context);
};
