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

import java.io.IOException;
import org.datagator.tools.importer.AtomType;
import org.datagator.tools.importer.Extractor;

/**
 * Helper extractor that chains multiple extractors.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/09/30
 */
public class ChainExtractor implements Extractor {

    private final Extractor[] _chainExtractors;
    private int _cursor;

    public ChainExtractor(Extractor[] extractors) {
        _chainExtractors = extractors;
        _cursor = 0;
    }

    @Override
    public AtomType nextAtom() throws IOException {
        AtomType token = null;
        if (_cursor < _chainExtractors.length) {
            token = _chainExtractors[_cursor].nextAtom();
            while (token == null) {
                if (++_cursor >= _chainExtractors.length) {
                    break;
                }
                token = _chainExtractors[_cursor].nextAtom();
            }
        }
        return token;
    }

    @Override
    public AtomType getCurrentAtomType() {
        if (_cursor < _chainExtractors.length) {
            return _chainExtractors[_cursor].getCurrentAtomType();
        }
        return null;
    }

    @Override
    public Object getCurrentAtomData() {
        if (_cursor < _chainExtractors.length) {
            return _chainExtractors[_cursor].getCurrentAtomData();
        }
        return null;
    }

}
