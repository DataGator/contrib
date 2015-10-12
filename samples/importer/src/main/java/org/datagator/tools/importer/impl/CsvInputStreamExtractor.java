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
package org.datagator.tools.importer.impl;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.dataformat.csv.CsvFactory;
import com.fasterxml.jackson.dataformat.csv.CsvParser;
import java.io.IOException;
import java.io.InputStream;
import java.math.BigDecimal;
import java.math.BigInteger;
import org.datagator.tools.importer.AtomType;
import org.datagator.tools.importer.InputStreamExtractor;

/**
 * Extract data from CSV input stream.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/30
 */
class CsvInputStreamExtractor extends InputStreamExtractor {

    protected static final CsvFactory csv = new CsvFactory();
    
    private final CsvParser _parser;
    private AtomType _atom = null;
    private Object _data = null;
    private int _numFields = 0;

    public CsvInputStreamExtractor(InputStream stream) throws IOException {
        super(stream);
        _parser = csv.createParser(this.stream);
    }

    @Override
    public AtomType nextAtom() throws IOException {
        JsonToken token = _parser.nextToken();
        while (token != null) {
            switch (token) {
                case START_ARRAY:
                    _numFields = 0;
                    _data = null;
                    return _atom = AtomType.START_RECORD;
                case END_ARRAY:
                    _data = _numFields;
                    return _atom = AtomType.END_RECORD;
                case VALUE_STRING:
                    _numFields += 1;
                    String raw = _parser.getText();
                    if (raw == null || raw.isEmpty()) {
                        _data = null;
                        return _atom = AtomType.NULL;
                    }
                    try {
                        switch (_parser.getNumberType()) {
                            case INT:
                            case LONG:
                                _data = Long.parseLong(raw);
                                return _atom = AtomType.INTEGER;
                            case BIG_INTEGER:
                                _data = new BigInteger(raw);
                                return _atom = AtomType.INTEGER;
                            case FLOAT:
                            case DOUBLE:
                                _data = Double.parseDouble(raw);
                                return _atom = AtomType.FLOAT;
                            case BIG_DECIMAL:
                                _data = new BigDecimal(raw);
                                return _atom = AtomType.FLOAT;
                            default:
                                break;
                        }
                    } catch (JsonParseException ioe) {
                        ; // this can be silently ignored
                    }
                    _data = raw;
                    return _atom = AtomType.STRING;
                case VALUE_NULL:
                    _data = null;
                    return _atom = AtomType.NULL;
                case START_OBJECT:
                case END_OBJECT:
                case FIELD_NAME:
                case VALUE_EMBEDDED_OBJECT:
                case VALUE_NUMBER_INT:
                case VALUE_NUMBER_FLOAT:
                case VALUE_TRUE:
                case VALUE_FALSE:
                case NOT_AVAILABLE:
                default:
                    break;
            }
            token = _parser.nextToken();
        }
        _data = null;
        return this._atom = null;
    }

    @Override
    public AtomType getCurrentAtomType() {
        return _atom;
    }

    @Override
    public Object getCurrentAtomData() {
        return _data;
    }

}
