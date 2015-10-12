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
 * Helper extractor that returns a single START_GROUP or END_GROUP token.
 *
 * @author LIU Yu <liuyu@opencps.net>
 * @date 2015/10/02
 */
public abstract class GroupExtractor implements Extractor {

    public static class StartGroup extends GroupExtractor {

        @Override
        public AtomType getCurrentAtomType() {
            return AtomType.START_GROUP;
        }

    }

    public static class EndGroup extends GroupExtractor {

        @Override
        public AtomType getCurrentAtomType() {
            return AtomType.END_GROUP;
        }
    }

    private boolean _once = true;

    @Override
    public AtomType nextAtom() throws IOException {
        if (_once) {
            _once = false;
            return getCurrentAtomType();
        }
        return null;
    }
    
    @Override
    public Object getCurrentAtomData() {
        return null;
    }

}
