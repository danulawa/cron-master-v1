function updateDescription() {
    const cronExpression = $("#cronExpression").val();
    const formatType = $("#cronType").val();

    $.ajax({
        url: "/explain",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({ expression: cronExpression, format_type: formatType }),
        success: function(response) {
            $("#description").text(response.explanation);
        },
        error: function() {
            $("#description").text("Error retrieving description. Please try again.");
        }
    });
}



$(document).ready(function() {
    const formatPlaceholders = {
        standard: "0 * * * *",
        quartz: "0 50 23 * * ?",
        aws: "0 * * * * *",
        spring: "0 * * * * *"
    };

    const defaultFormat = "quartz";
    $("#cronType").val(defaultFormat);
    $("#cronExpression").attr("placeholder", formatPlaceholders[defaultFormat]);
    $("#cronExpression").val(formatPlaceholders[defaultFormat]);
    updateDescription();

    $("#cronType").on("change", function() {
        const format = $(this).val();
        $("#cronExpression").attr("placeholder", formatPlaceholders[format]);
        $("#cronExpression").val(formatPlaceholders[format]);
        updateDescription();
    });

    $("#cronExpression").on("input", updateDescription);
    $("#cronType").on("change", updateDescription);
});




document.addEventListener('DOMContentLoaded', function () {
    const footer = document.querySelector('footer');

    function updateFooterClass() {
        if (document.documentElement.scrollHeight > document.documentElement.clientHeight) {
            footer.classList.remove('footer-1');
            footer.classList.add('footer-2');
        } else {
            footer.classList.remove('footer-2');
            footer.classList.add('footer-1');
        }
    }

    updateFooterClass();
    window.addEventListener('resize', updateFooterClass);
});

document.querySelector('.copy-icon').addEventListener('click', function () {
    const inputElement = document.getElementById('cronExpression');
    
    // Select the text inside the input
    inputElement.select();
    inputElement.setSelectionRange(0, 99999); // For mobile devices

    // Copy the text to the clipboard
    navigator.clipboard.writeText(inputElement.value)
        .then(() => {
            alert('Text copied to clipboard: ' + inputElement.value); // Optional feedback
        })
        .catch(err => {
            console.error('Failed to copy text: ', err);
        });
});

document.addEventListener('DOMContentLoaded', () => {
    const cronTypeDropdown = document.getElementById('cronType');
    const componentContainer = document.getElementById('componentContainer');

    const components = {
        standard: 'comp_standard',
        quartz: 'comp_quartz',
        aws: 'comp_aws',
        spring: 'comp_spring',
    };

    // Function to show the selected component and hide others
    const showComponent = (selectedComponent) => {
        for (const key in components) {
            const element = document.getElementById(components[key]);
            if (key === selectedComponent) {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        }
    };

    // Set the initial format dynamically
    const initialFormat = 'quartz'; // Change this value to set the desired default format
    cronTypeDropdown.value = initialFormat;
    showComponent(initialFormat); // Show initial component

    // Update component based on selected value
    cronTypeDropdown.addEventListener('change', () => {
        const selectedValue = cronTypeDropdown.value;
        showComponent(selectedValue); // Show corresponding component
    });
});


