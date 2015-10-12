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

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonSubTypes.Type;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.IOException;
import java.io.Reader;
import org.datagator.api.client.backend.DataGatorService;

/**
 * Client-side data binding of DataGator entities.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/01
 */
@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.PROPERTY,
    property = "kind")
@JsonSubTypes({
    @Type(name = "datagator#Repo", value = Repo.class),
    @Type(name = "datagator#DataSet", value = DataSet.class),
    @Type(name = "datagator#Matrix", value = SimpleMatrix.class)
})
public abstract class Entity
{

    protected static final DataGatorService service = new DataGatorService();

    protected static final JsonFactory json;

    static {
        json = new JsonFactory();
        ObjectMapper mapper = new ObjectMapper();
        json.setCodec(mapper);
    }

    public final String kind;

    @JsonCreator
    protected Entity(@JsonProperty("kind") String kind)
    {
        assert (kind.startsWith("datagator#"));
        this.kind = kind.substring("datagator#".length());
    }

    public static Entity create(Reader reader)
        throws IOException
    {
        JsonParser parser = json.createParser(reader);
        return parser.readValueAs(Entity.class);
    }
}
