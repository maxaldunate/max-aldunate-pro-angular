'use strict';

console.log('Loading function');
let doc = require('dynamodb-doc');
let dynamo = new doc.DynamoDB();

const createResponse = (statusCode, body) => {
    return {
        "statusCode": statusCode,
        "body": body || ""
    }
};

exports.getById = (event, context, callback) => {

    var params = {
        "TableName": "lg-courses",
    };
    
    dynamo.getItem(params, (err, data) => {
        var response;
        if (err)
            response = createResponse(500, err);
        else
            response = createResponse(200, data.Item ? data.Item.doc : null);
        callback(null, response);
    });
};
