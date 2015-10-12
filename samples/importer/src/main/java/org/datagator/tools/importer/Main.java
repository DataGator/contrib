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
package org.datagator.tools.importer;

import javax.xml.xpath.XPathExpression;
import com.fasterxml.jackson.core.JsonEncoding;
import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonGenerator;
import java.io.File;
import java.io.IOException;
import java.util.logging.Logger;
import org.datagator.tools.importer.impl.FileExtractor;
import org.datagator.utils.json.StandardPrinter;

/**
 * CLI Interface of DataGator Importer.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/10/02
 */
public class Main {

    private static final Logger log = Logger.getLogger(
            "org.datagator.tools.importer");

    private static final JsonFactory json = new JsonFactory();

    static {
        json.configure(JsonGenerator.Feature.ESCAPE_NON_ASCII, true);
    }

    public static void main(String[] args) throws IOException {
        JsonGenerator jg = json.createGenerator(System.out, JsonEncoding.UTF8);
        jg.setPrettyPrinter(new StandardPrinter());

        Extractor extractor = new FileExtractor(new File(args[0]));

        int columnHeaders = 1; // TODO: cli input
        int rowHeaders = 3; // TODO: cli input

        int columnsCount = -1;

        AtomType token = extractor.nextAtom();
        while (token != null) {
            switch (token) {
                case FLOAT:
                case INTEGER:
                case STRING:
                case NULL:
                    jg.writeObject(extractor.getCurrentAtomData());
                    break;
                case START_RECORD:
                    jg.writeStartArray();
                    break;
                case END_RECORD:
                    int _numFields = (Integer) extractor.getCurrentAtomData();
                    if (columnsCount < 0) {
                        columnsCount = _numFields;
                    } else if (columnsCount != _numFields) {
                        throw new RuntimeException(String.format(
                                "row %s has different length than previous rows",
                                String.valueOf(_numFields - 1)));
                    }
                    jg.writeEndArray();
                    break;
                case START_GROUP:
                    jg.writeStartObject();
                    jg.writeStringField("kind", "datagator#Matrix");
                    jg.writeNumberField("columnHeaders", columnHeaders);
                    jg.writeNumberField("rowHeaders", rowHeaders);
                    jg.writeFieldName("rows");
                    jg.writeStartArray();
                    break;
                case END_GROUP:
                    int rowsCount = (Integer) extractor.getCurrentAtomData();
                    if (rowsCount == 0) {
                        jg.writeStartArray();
                        jg.writeEndArray();
                        rowsCount = 1;
                        columnsCount = 0;
                    }
                    jg.writeEndArray();
                    jg.writeNumberField("rowsCount", rowsCount);
                    jg.writeNumberField("columnsCount", columnsCount);
                    jg.writeEndObject();
                    break;
                default:
                    break;
            }
            token = extractor.nextAtom();
        }

        jg.close();
    }

}
