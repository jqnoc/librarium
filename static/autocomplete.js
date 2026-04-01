// ═══════════════════════════════════════════════════════════════════════════
// Librarium — Custom autocomplete for input[list] elements
//
// Replaces the unreliable native <datalist> behaviour with a custom dropdown
// that opens on a single click and re-opens after typing "; " for multi-value
// fields.
// ═══════════════════════════════════════════════════════════════════════════
(function () {
    'use strict';

    function initAutocomplete(input) {
        var listId = input.getAttribute('list');
        if (!listId) return;

        var datalist = document.getElementById(listId);
        if (!datalist) return;

        // Collect options from the datalist and detach the native behaviour
        var allOptions = Array.from(datalist.querySelectorAll('option')).map(function (o) {
            return o.value;
        });
        input.removeAttribute('list');

        // ── Build the floating dropdown ───────────────────────────────
        var dropdown = document.createElement('ul');
        dropdown.className = 'lb-autocomplete-dropdown';
        document.body.appendChild(dropdown);

        var activeFocus = -1;

        // ── Helpers ───────────────────────────────────────────────────

        /** For "a; b; c" return "c" (the segment being typed). */
        function currentSegment(text) {
            var segs = text.split(';');
            return segs[segs.length - 1].replace(/^\s+/, '');
        }

        /** Everything before the last segment, ready to be prepended. */
        function basePrefix(text) {
            var last = text.lastIndexOf(';');
            if (last === -1) return '';
            return text.substring(0, last + 1) + ' ';
        }

        function positionDropdown() {
            var rect = input.getBoundingClientRect();
            dropdown.style.left = (rect.left + window.scrollX) + 'px';
            dropdown.style.top  = (rect.bottom + window.scrollY + 2) + 'px';
            dropdown.style.width = rect.width + 'px';
        }

        function showDropdown(filter) {
            dropdown.innerHTML = '';
            activeFocus = -1;

            var lower = (filter || '').toLowerCase();
            var matches = allOptions.filter(function (opt) {
                return !lower || opt.toLowerCase().indexOf(lower) !== -1;
            });

            if (matches.length === 0) {
                dropdown.style.display = 'none';
                return;
            }

            matches.forEach(function (opt) {
                var li = document.createElement('li');
                li.className = 'lb-autocomplete-item';
                li.textContent = opt;
                li.addEventListener('mousedown', function (e) {
                    e.preventDefault();                 // don't blur the input
                    input.value = basePrefix(input.value) + opt;
                    hideDropdown();
                    input.focus();
                });
                dropdown.appendChild(li);
            });

            positionDropdown();
            dropdown.style.display = 'block';
        }

        function hideDropdown() {
            dropdown.style.display = 'none';
            activeFocus = -1;
        }

        function markActive() {
            var items = dropdown.querySelectorAll('.lb-autocomplete-item');
            items.forEach(function (item, i) {
                item.classList.toggle('lb-autocomplete-active', i === activeFocus);
            });
            if (activeFocus >= 0 && items[activeFocus]) {
                items[activeFocus].scrollIntoView({ block: 'nearest' });
            }
        }

        // ── Events ────────────────────────────────────────────────────

        // Single click or focus → open
        input.addEventListener('click', function () {
            showDropdown(currentSegment(this.value));
        });
        input.addEventListener('focus', function () {
            showDropdown(currentSegment(this.value));
        });

        // Typing → filter; after "; " reopen for next value
        input.addEventListener('input', function () {
            showDropdown(currentSegment(this.value));
        });

        // Keyboard navigation
        input.addEventListener('keydown', function (e) {
            if (dropdown.style.display === 'none') {
                if (e.key === 'ArrowDown') { showDropdown(currentSegment(this.value)); }
                return;
            }
            var items = dropdown.querySelectorAll('.lb-autocomplete-item');
            switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                activeFocus = Math.min(activeFocus + 1, items.length - 1);
                markActive();
                break;
            case 'ArrowUp':
                e.preventDefault();
                activeFocus = Math.max(activeFocus - 1, 0);
                markActive();
                break;
            case 'Enter':
                if (activeFocus >= 0 && items[activeFocus]) {
                    e.preventDefault();
                    items[activeFocus].dispatchEvent(new MouseEvent('mousedown'));
                }
                break;
            case 'Escape':
                hideDropdown();
                break;
            }
        });

        // Blur → hide (delay allows mousedown on item to fire first)
        input.addEventListener('blur', function () {
            setTimeout(hideDropdown, 150);
        });

        // Re-position if the window scrolls while dropdown is open
        window.addEventListener('scroll', function () {
            if (dropdown.style.display !== 'none') positionDropdown();
        }, true);
    }

    function init() {
        document.querySelectorAll('input[list]').forEach(function (input) {
            initAutocomplete(input);
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
