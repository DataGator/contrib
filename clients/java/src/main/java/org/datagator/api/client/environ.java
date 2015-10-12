/*
 * Copyright 2015 by University of Denver <http://pardee.du.edu/>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 * WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.datagator.api.client;

import java.util.MissingResourceException;
import java.util.ResourceBundle;

/**
 * Collector of client-side environment and resource bundle variables
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/01
 */
public final class environ {

    private static final ResourceBundle RESOURCE_BUNDLE = ResourceBundle
            .getBundle("org.datagator.api.client");

    private static String get(String key, String default_value) {
        String value = System.getenv(key);
        if (value != null) {
            return value;
        } else {
            try {
                value = RESOURCE_BUNDLE.getString(key);
            } catch (MissingResourceException e) {
                value = default_value;
            }
        }
        return value;
    }

    private static String get(String key) {
        return get(key, null);
    }

    public static final String DATAGATOR_API_CLIENT_VERSION = get(
            "DATAGATOR_API_CLIENT_VERSION");

    public static final String DATAGATOR_API_HOST = get("DATAGATOR_API_HOST",
            "www.data-gator.com");

    public static final String DATAGATOR_API_SCHEME = get(
            "DATAGATOR_API_SCHEME", "https");

    public static final int DATAGATOR_API_PORT = Integer
            .parseInt(get("DATAGATOR_API_PORT", "80"));

    public static final String DATAGATOR_API_VERSION = get(
            "DATAGATOR_API_VERSION", "v2");

    /**
     * relative URI (relative to site root)
     */
    public static final String DATAGATOR_API_URL_PREFIX;

    /**
     * absolute URI
     */
    public static final String DATAGATOR_API_URL;

    /**
     * user agent HTTP header
     */
    public static final String DATAGATOR_API_USER_AGENT;

    /**
     * credentials in the form <code>key</code>, <code>secret</code>
     */
    public static final String DATAGATOR_CREDENTIALS;

    public static final boolean DEBUG = Boolean.parseBoolean(get("DEBUG",
            "false"));

    static {

        DATAGATOR_API_URL_PREFIX = String.format("/api/%s",
                DATAGATOR_API_VERSION);

        DATAGATOR_API_URL = String.format("%s://%s%s",
                DATAGATOR_API_SCHEME, DATAGATOR_API_HOST, DATAGATOR_API_URL_PREFIX);

        DATAGATOR_API_USER_AGENT = String.format(
                "datagator-api-client (java/%s)", DATAGATOR_API_CLIENT_VERSION);

        // skip the resource bundle and directly query the environment
        DATAGATOR_CREDENTIALS = System.getenv("DATAGATOR_CREDENTIALS");
    }
}
