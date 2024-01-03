(function () {

    var dialectInfo = {};

    function updateDialect(newValue) {
        const desiredDialect = `dialect-${newValue}`;
        const caseInfo = dialectInfo[newValue].examples;
        const dialectDefinitions = document.querySelectorAll('.dialect-definition');
        for (var dialectDefinition of dialectDefinitions) {
            if (dialectDefinition.id == desiredDialect) {
                dialectDefinition.removeAttribute('hidden');
            } else {
                dialectDefinition.setAttribute('hidden', '');
            }
        }

        const cases = document.querySelectorAll('.bft-case');
        const errMessages = document.querySelectorAll('.bft-case-err-message');

        for (let i = 0; i < caseInfo.length; i++) {
            const case_msg = caseInfo[i];
            if (case_msg == null) {
                cases[i].classList.remove("bft-error-case");
                errMessages[i].setAttribute("hidden", "");
            } else {
                cases[i].classList.add("bft-error-case");
                errMessages[i].removeAttribute("hidden");
                errMessages[i].querySelector("td").innerText = case_msg;
            }
        }

        const kernelInfo = dialectInfo[newValue].kernels;
        const kernelItems = document.querySelectorAll('.bft-kernel');
        for (let i = 0; i < kernelInfo.length; i++) {
            const kernelSpans = kernelItems[i].querySelectorAll('span');
            if (kernelInfo[i]) {
                kernelSpans[0].classList.remove('bft-unsupported-kernel');
                kernelSpans[1].setAttribute('hidden', '');
            } else {
                kernelSpans[0].classList.add('bft-unsupported-kernel');
                kernelSpans[1].removeAttribute('hidden');
            }
        }
    }

    window.bftInitialize = function (functionDialectInfo) {
        dialectInfo = functionDialectInfo;
        const dialectSelect = document.getElementById('dialect');
        updateDialect(dialectSelect.value);
        dialectSelect.addEventListener('change', (e) => {
            updateDialect(e.target.value);
        });
    }

})();
