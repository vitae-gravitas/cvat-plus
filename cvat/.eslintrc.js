/*
 * Copyright (C) 2018 Intel Corporation
 *
 * SPDX-License-Identifier: MIT
 */

 module.exports = {
    "env": {
        "node": false,
        "browser": true,
        "es6": true,
        "jquery": true,
        "qunit": true,
    },
    "parserOptions": {
        "sourceType": "script",
    },
    "plugins": [
        "security",
        "no-unsanitized",
        "no-unsafe-innerhtml",
    ],
    "extends": [
        "eslint:recommended",
        "plugin:security/recommended",
        "plugin:no-unsanitized/DOM",
        "airbnb",
    ],
    "rules": {
        "no-new": [0],
        "class-methods-use-this": [0],
        "no-restricted-properties": [0, {
            "object": "Math",
            "property": "pow",
        }],
        "no-param-reassign": [0],
        "no-underscore-dangle": ["error", { "allowAfterThis": true }],
        "no-restricted-syntax": [0, {"selector": "ForOfStatement"}],
        "no-continue": [0],
        "no-unsafe-innerhtml/no-unsafe-innerhtml": 1,
        // This rule actual for user input data on the node.js environment mainly.
        "security/detect-object-injection": 0,
        "indent": ["warn", 4],
    },
};
