$(document).ready(function () {
    $('.clickable-row').on('click', function () {
        window.location = $(this).data('href')
    })

    const dataTable = new DataTable('#queueTable', {
        // not specifying a width for the first column makes it take up as much space as is available.
        columns: [null, {width: '15%'}, {width: '15%'}, {width: '15%'}, {width: '10%'}, {width: '10%'}],
        responsive: {
            details: false,
        },
        columnDefs: [
            { responsivePriority: 1, targets: [0] },
            { responsivePriority: 2, targets: [2] },
            {
                targets: [0],
                columnControl: ['order', ['colVis']]
            },
            {
                targets: [1, 2, 3],
                columnControl: ['order', ['searchList']]
            },
            {
                targets: [4],
                columnControl: ['order'],
                className: 'dt-left',
            },
        ],
        ordering: {
            indicators: false,
            handler: false
        },
        scrollX: true,
    });
})