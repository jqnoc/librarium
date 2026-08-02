(function () {
    function byId(id) {
        return document.getElementById(id);
    }

    function setDisplay(id, display) {
        var element = byId(id);
        if (element) element.style.display = display;
    }

    window.toggleFormatFields = function () {
        var format = byId('format');
        if (!format) return;
        var value = format.value;
        var isAudiobook = value === 'audiobook';
        setDisplay('binding-fields', value === 'paper' ? '' : 'none');
        setDisplay('audio-format-fields', isAudiobook ? '' : 'none');
        setDisplay('pages-row', isAudiobook ? 'none' : '');
        setDisplay('total-time-row', isAudiobook ? '' : 'none');
        setDisplay('frontmatter-group', isAudiobook ? 'none' : '');

        var binding = byId('binding');
        if (binding) binding.disabled = value !== 'paper';
        var audioFormat = byId('audio_format');
        if (audioFormat) audioFormat.disabled = !isAudiobook;
        var pages = byId('pages');
        if (pages) pages.disabled = isAudiobook;
        ['total_time_hours', 'total_time_minutes', 'total_time_seconds'].forEach(function (id) {
            var input = byId(id);
            if (input) input.disabled = !isAudiobook;
        });
        var startingPage = byId('starting_page');
        if (startingPage) startingPage.disabled = isAudiobook;
    };

    window.toggleSourceFields = function () {
        var selectedInput = document.querySelector('input[name="source_type"]:checked');
        if (!selectedInput) return;
        var selected = selectedInput.value;
        setDisplay('owned-fields', selected === 'owned' ? 'block' : 'none');
        setDisplay('borrowed-fields', selected === 'borrowed' ? 'block' : 'none');

        var owned = byId('source_id_owned');
        var gift = byId('source_id_gift');
        var borrowed = byId('source_id_borrowed');
        if (owned) owned.disabled = true;
        if (gift) gift.disabled = true;
        if (borrowed) borrowed.disabled = selected !== 'borrowed';
        if (selected === 'owned') window.toggleGiftFields();
        if (selected !== 'owned') {
            var giftCheckbox = byId('is_gift');
            if (giftCheckbox) giftCheckbox.checked = false;
        }
    };

    window.toggleGiftFields = function () {
        var giftCheckbox = byId('is_gift');
        if (!giftCheckbox) return;
        var isGift = giftCheckbox.checked;
        var translate = window.librariumI18n ? window.librariumI18n.t : function (key) { return key; };
        var dateLabel = byId('label_purchase_date');
        var placeLabel = byId('label_source_id_owned');
        if (dateLabel) {
            dateLabel.textContent = isGift ? translate('bookForm.dateReceived') : translate('bookForm.purchaseDate');
            dateLabel.setAttribute('data-i18n', isGift ? 'bookForm.dateReceived' : 'bookForm.purchaseDate');
        }
        if (placeLabel) {
            placeLabel.textContent = isGift ? translate('bookForm.giftFrom') : translate('bookForm.purchasePlace');
            placeLabel.setAttribute('data-i18n', isGift ? 'bookForm.giftFrom' : 'bookForm.purchasePlace');
        }
        setDisplay('price-row', isGift ? 'none' : '');
        setDisplay('source_id_owned', isGift ? 'none' : '');
        setDisplay('source_id_gift', isGift ? '' : 'none');
        var owned = byId('source_id_owned');
        var gift = byId('source_id_gift');
        if (owned) owned.disabled = isGift;
        if (gift) gift.disabled = !isGift;
    };

    function normalize(value) {
        return (value || '').trim().replace(/\s+/g, ' ');
    }

    function compareValues(leftValue, rightValue) {
        return leftValue.localeCompare(rightValue, undefined, { sensitivity: 'base' });
    }

    function initClassificationEditor(editor) {
        if (editor.dataset.initialized) return;
        editor.dataset.initialized = 'true';

        var field = editor.dataset.field;
        var hidden = byId(field);
        var input = editor.querySelector('[data-chip-input]');
        var chips = editor.querySelector('[data-chips-container]');
        var suggestionsBox = editor.querySelector('[data-classification-suggestions]');
        if (!hidden || !input || !chips || !suggestionsBox) return;
        var suggestions = Array.from(document.querySelectorAll('#' + field + '-list option')).map(function (option) {
            return normalize(option.value);
        }).filter(Boolean).sort(compareValues);
        var visibleSuggestions = [];
        var activeSuggestion = -1;

        function values() {
            return Array.from(chips.querySelectorAll('.classification-chip-label')).map(function (label) {
                return normalize(label.textContent);
            }).filter(Boolean);
        }

        function sync() {
            hidden.value = values().join('; ');
        }

        function sortChips() {
            Array.from(chips.querySelectorAll('.classification-chip'))
                .sort(function (leftChip, rightChip) {
                    var leftLabel = leftChip.querySelector('.classification-chip-label');
                    var rightLabel = rightChip.querySelector('.classification-chip-label');
                    return compareValues(
                        normalize(leftLabel && leftLabel.textContent),
                        normalize(rightLabel && rightLabel.textContent)
                    );
                })
                .forEach(function (chip) {
                    chips.appendChild(chip);
                });
        }

        function removeDuplicateChips() {
            var seen = {};
            Array.from(chips.querySelectorAll('.classification-chip')).forEach(function (chip) {
                var label = chip.querySelector('.classification-chip-label');
                var value = normalize(label && label.textContent);
                var key = value.toLowerCase();
                if (!value || seen[key]) {
                    chip.remove();
                    return;
                }
                seen[key] = true;
            });
            sortChips();
        }

        function hideSuggestions() {
            suggestionsBox.innerHTML = '';
            suggestionsBox.classList.remove('is-open');
            suggestionsBox.setAttribute('aria-expanded', 'false');
            visibleSuggestions = [];
            activeSuggestion = -1;
            input.removeAttribute('aria-activedescendant');
        }

        function updateActiveSuggestion() {
            Array.from(suggestionsBox.querySelectorAll('[role="option"]')).forEach(function (item, index) {
                item.classList.toggle('is-active', index === activeSuggestion);
                item.setAttribute('aria-selected', index === activeSuggestion ? 'true' : 'false');
            });
            if (activeSuggestion >= 0 && visibleSuggestions[activeSuggestion]) {
                input.setAttribute('aria-activedescendant', field + '-suggestion-' + activeSuggestion);
            } else {
                input.removeAttribute('aria-activedescendant');
            }
        }

        function renderSuggestions() {
            var typed = normalize(input.value).toLowerCase();
            var existing = values().map(function (value) { return value.toLowerCase(); });
            visibleSuggestions = suggestions.filter(function (value) {
                var lower = value.toLowerCase();
                return (!typed || lower.indexOf(typed) !== -1) && existing.indexOf(lower) === -1;
            });
            suggestionsBox.innerHTML = '';
            activeSuggestion = -1;
            if (!visibleSuggestions.length) {
                hideSuggestions();
                return;
            }
            visibleSuggestions.forEach(function (value, index) {
                var item = document.createElement('div');
                item.className = 'classification-suggestion';
                item.id = field + '-suggestion-' + index;
                item.setAttribute('role', 'option');
                item.setAttribute('aria-selected', 'false');
                item.textContent = value;
                item.addEventListener('mousedown', function (event) {
                    event.preventDefault();
                    addValue(value);
                    input.value = '';
                    sync();
                    hideSuggestions();
                    input.focus();
                });
                suggestionsBox.appendChild(item);
            });
            suggestionsBox.classList.add('is-open');
            suggestionsBox.setAttribute('aria-expanded', 'true');
        }

        function addValue(value) {
            var normalized = normalize(value);
            if (!normalized || values().some(function (item) {
                return item.toLowerCase() === normalized.toLowerCase();
            })) return;
            var chip = document.createElement('span');
            chip.className = 'classification-chip';
            var label = document.createElement('span');
            label.className = 'classification-chip-label';
            label.textContent = normalized;
            var remove = document.createElement('button');
            remove.type = 'button';
            remove.className = 'classification-chip-remove';
            remove.setAttribute('data-remove-chip', '');
            remove.setAttribute('aria-label', 'Remove ' + normalized);
            remove.textContent = '\u00d7';
            chip.appendChild(label);
            chip.appendChild(remove);
            chips.appendChild(chip);
            sortChips();
        }

        function addInputValue(keepFocus) {
            input.value.split(';').forEach(addValue);
            input.value = '';
            sync();
            if (keepFocus !== false) input.focus();
            renderSuggestions();
        }

        input.setAttribute('aria-autocomplete', 'list');
        input.setAttribute('aria-controls', suggestionsBox.id);
        suggestionsBox.setAttribute('aria-expanded', 'false');
        removeDuplicateChips();
        sync();
        input.addEventListener('focus', renderSuggestions);
        input.addEventListener('click', renderSuggestions);
        input.addEventListener('input', function () {
            if (input.value.indexOf(';') !== -1) {
                addInputValue();
                return;
            }
            renderSuggestions();
        });
        input.addEventListener('keydown', function (event) {
            if (event.key === 'ArrowDown' && visibleSuggestions.length) {
                event.preventDefault();
                activeSuggestion = Math.min(activeSuggestion + 1, visibleSuggestions.length - 1);
                updateActiveSuggestion();
            } else if (event.key === 'ArrowUp' && visibleSuggestions.length) {
                event.preventDefault();
                activeSuggestion = Math.max(activeSuggestion - 1, 0);
                updateActiveSuggestion();
            } else if (event.key === 'Enter') {
                event.preventDefault();
                if (activeSuggestion >= 0 && visibleSuggestions[activeSuggestion]) {
                    addValue(visibleSuggestions[activeSuggestion]);
                    input.value = '';
                    sync();
                    hideSuggestions();
                    renderSuggestions();
                } else {
                    addInputValue();
                }
            } else if (event.key === ';') {
                event.preventDefault();
                addInputValue();
            } else if (event.key === 'Backspace' && !input.value.trim()) {
                var current = chips.lastElementChild;
                if (current) {
                    current.remove();
                    sync();
                    renderSuggestions();
                }
            } else if (event.key === 'Escape') {
                hideSuggestions();
            }
        });
        input.addEventListener('blur', function () {
            setTimeout(function () {
                if (input.value.trim()) addInputValue(false);
                hideSuggestions();
            }, 120);
        });
        chips.addEventListener('click', function (event) {
            var remove = event.target.closest('[data-remove-chip]');
            if (!remove) return;
            remove.closest('.classification-chip').remove();
            sync();
            renderSuggestions();
            input.focus();
        });
        editor.addEventListener('click', function (event) {
            if (event.target === editor || event.target === chips) input.focus();
        });
        var form = editor.closest('form');
        if (form) {
            form.addEventListener('submit', function () {
                if (input.value.trim()) addInputValue(false);
                sync();
            });
        }
    }

    function initialize() {
        if (window.flatpickr) {
            window.flatpickr('#purchase_date, #borrowed_start, #borrowed_end', {
                dateFormat: 'Y-m-d',
                altInput: true,
                altFormat: 'd/m/Y',
                allowInput: true
            });
        }
        window.toggleFormatFields();
        window.toggleSourceFields();
        document.querySelectorAll('[data-classification-editor]').forEach(initClassificationEditor);
        var addSeriesButton = byId('add-series-btn');
        if (addSeriesButton) {
            addSeriesButton.addEventListener('click', function () {
                var template = byId('series-row-template');
                var entries = byId('series-entries');
                if (!template || !entries) return;
                entries.appendChild(template.content.cloneNode(true));
                if (window.librariumI18n) window.librariumI18n.apply();
            });
        }
    }

    initialize();
}());
