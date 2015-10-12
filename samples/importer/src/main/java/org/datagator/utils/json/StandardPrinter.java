/*
 * Copyright 2015 University of Denver <http://pardee.du.edu/>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
package org.datagator.utils.json;

import com.fasterxml.jackson.core.JsonGenerationException;
import com.fasterxml.jackson.core.JsonGenerator;
import com.fasterxml.jackson.core.PrettyPrinter;
import java.io.IOException;

/**
 * Parsing Canonical Form (PCF) Printer for JSON documents.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/10/02
 */
public class StandardPrinter implements PrettyPrinter {

    @Override
    public void writeRootValueSeparator(JsonGenerator jg) throws IOException, JsonGenerationException {
        ; // no output
    }

    @Override
    public void writeStartObject(JsonGenerator jg) throws IOException, JsonGenerationException {
        jg.writeRaw("{");
    }

    @Override
    public void writeEndObject(JsonGenerator jg, int nrOfEntries) throws IOException, JsonGenerationException {
        jg.writeRaw("}");
    }

    @Override
    public void writeObjectEntrySeparator(JsonGenerator jg) throws IOException, JsonGenerationException {
        jg.writeRaw(", ");
    }

    @Override
    public void writeObjectFieldValueSeparator(JsonGenerator jg) throws IOException, JsonGenerationException {
        jg.writeRaw(": ");
    }

    @Override
    public void writeStartArray(JsonGenerator jg) throws IOException, JsonGenerationException {
        jg.writeRaw("[");
    }

    @Override
    public void writeEndArray(JsonGenerator jg, int nrOfValues) throws IOException, JsonGenerationException {
        jg.writeRaw("]");
    }

    @Override
    public void writeArrayValueSeparator(JsonGenerator jg) throws IOException, JsonGenerationException {
        jg.writeRaw(", ");
    }

    @Override
    public void beforeArrayValues(JsonGenerator jg) throws IOException, JsonGenerationException {
        ; // no output
    }

    @Override
    public void beforeObjectEntries(JsonGenerator jg) throws IOException, JsonGenerationException {
        ; // no output
    }
    
}
