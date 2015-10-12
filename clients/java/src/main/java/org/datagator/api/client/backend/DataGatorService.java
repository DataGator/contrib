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
package org.datagator.api.client.backend;

import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.security.KeyManagementException;
import java.security.NoSuchAlgorithmException;
import java.util.logging.Logger;

import javax.net.ssl.SSLContext;

import com.fasterxml.jackson.core.JsonFactory;

import org.apache.commons.io.IOUtils;

import org.apache.http.HttpHost;
import org.apache.http.HttpEntity;
import org.apache.http.auth.AuthScope;
import org.apache.http.auth.UsernamePasswordCredentials;
import org.apache.http.client.AuthCache;
import org.apache.http.client.CredentialsProvider;
import org.apache.http.client.methods.CloseableHttpResponse;
import org.apache.http.client.methods.HttpGet;
import org.apache.http.client.methods.HttpPatch;
import org.apache.http.client.protocol.HttpClientContext;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.conn.ssl.SSLConnectionSocketFactory;
import org.apache.http.impl.conn.PoolingHttpClientConnectionManager;
import org.apache.http.entity.ContentType;
import org.apache.http.entity.InputStreamEntity;
import org.apache.http.impl.auth.BasicScheme;
import org.apache.http.impl.client.BasicAuthCache;
import org.apache.http.impl.client.BasicCredentialsProvider;
import org.apache.http.impl.client.CloseableHttpClient;
import org.apache.http.impl.client.HttpClients;
import org.apache.http.ssl.SSLContexts;

import org.datagator.api.client.environ;

/**
 * Low-level HTTP client to back-end web services
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/01
 */
public class DataGatorService
{

    private static final JsonFactory json = new JsonFactory();

    private static final CloseableHttpClient http;

    private static final Logger log = Logger.getLogger(
        "org.datagator.api.client.backend");

    static {
        // apply rate limit
        class ThrottleConnectionManager
            extends PoolingHttpClientConnectionManager
        {
        };

        // force TLSv1 protocol
        SSLConnectionSocketFactory ssl_factory = null;
        try {
            SSLContext ssl_context = SSLContexts.custom().build();
            ssl_factory = new SSLConnectionSocketFactory(ssl_context,
                new String[]{"TLSv1"}, null,
                SSLConnectionSocketFactory.getDefaultHostnameVerifier());
        } catch (KeyManagementException e) {
            log.severe(e.getMessage());
            System.exit(-1);
        } catch (NoSuchAlgorithmException e) {
            log.severe(e.getMessage());
            System.exit(-1);
        }
        // connection manager
        http = HttpClients.custom().setSSLSocketFactory(ssl_factory)
            .setConnectionManager(new ThrottleConnectionManager())
            .setUserAgent(environ.DATAGATOR_API_USER_AGENT).build();
    }

    private static URI buildServiceURI(String endpoint)
        throws URISyntaxException
    {
        URI uri = new URIBuilder().setScheme(environ.DATAGATOR_API_SCHEME)
            .setHost(environ.DATAGATOR_API_HOST)
            .setPath(environ.DATAGATOR_API_URL_PREFIX + endpoint).build();
        return uri;
    }

    private final HttpClientContext context;

    public DataGatorService()
    {
        super();
        log.info("Initializing service without authorization");
        this.context = HttpClientContext.create();
    }

    public DataGatorService(UsernamePasswordCredentials auth)
    {
        this();
        log.info(String.format("Initializing service with authorization: %s",
            auth.getUserName()));
        // attach credentials to context
        HttpHost host = new HttpHost(environ.DATAGATOR_API_HOST,
            environ.DATAGATOR_API_PORT, environ.DATAGATOR_API_SCHEME);
        AuthScope scope = new AuthScope(host.getHostName(), host.getPort());
        CredentialsProvider provider = new BasicCredentialsProvider();
        provider.setCredentials(scope, auth);
        this.context.setCredentialsProvider(provider);
        // enable preemptive (pro-active) basic authentication
        AuthCache cache = new BasicAuthCache();
        cache.put(host, new BasicScheme());
        this.context.setAuthCache(cache);
    }

    public CloseableHttpResponse get(String endpoint)
        throws URISyntaxException, IOException
    {
        HttpGet request = new HttpGet(buildServiceURI(endpoint));
        return http.execute(request, context);
    }

    public CloseableHttpResponse patch(String endpoint, InputStream data,
        ContentType ctype)
        throws URISyntaxException, IOException
    {
        HttpPatch request = new HttpPatch(buildServiceURI(endpoint));
        if (data != null) {
            HttpEntity entity = new InputStreamEntity(data, ctype);
            request.setEntity(entity);
        }
        return http.execute(request, context);
    }

    public CloseableHttpResponse patch(String endpoint, InputStream data)
        throws URISyntaxException, IOException
    {
        return patch(endpoint, data, ContentType.APPLICATION_JSON);
    }

    public static void main(String[] args)
        throws Exception
    {
        UsernamePasswordCredentials auth = null;
        String credentials = environ.DATAGATOR_CREDENTIALS;
        if (credentials != null) {
            String[] tuple = credentials.split(".", 1);
            if (tuple.length > 1) {
                auth = new UsernamePasswordCredentials(tuple[0], tuple[1]);
            } else if (tuple.length > 0) {
                auth = new UsernamePasswordCredentials(tuple[0], null);
            }
        }

        final DataGatorService service;
        if (auth != null) {
            service = new DataGatorService(auth);
        } else {
            service = new DataGatorService();
        }

        CloseableHttpResponse response = service.get("/");
        response.getEntity().writeTo(System.out);
        response.close();

        // JsonParser parser = json.createParser(stream);
    }
}
