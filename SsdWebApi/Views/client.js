function getAndShowForecastsByIndexId() {
    let indexId = $("#indexId").val();
    $.ajax({
        url: "https://localhost:5001/api/indici/" + indexId,
        type: "GET",
        contentType: "application/json",
        success: function(result) {
            console.log("received:");
            console.log(result);

            showForecastedSeries(JSON.parse(result));
            BtnReset($("#getForecastButton")); //remove spinner
            $("#forecastWaitingAlert").hide() //remove alert

        },
        error: handleError
    });
}

function getAndShowOptimalPortfolio() {
    console.log("btn pressed!")
    $.ajax({
        url: "https://localhost:5001/api/indici/portfolio",
        type: "GET",
        contentType: "application/json",
        success: function(result) {
            console.log("showing optimal portfolio:");
            console.log(result);

            showOptimalPortfolio(JSON.parse(result));
            BtnReset($("#getPortfolioButton")); //remove spinner
            $("#portfolioWaitingAlert").hide() //remove alert
        },
        error: handleError
    });
}

function handleError(xhr, status, p3, p4) {
    var err = "Error " + "" + status + "" + p3;
    if (xhr.responseText && xhr.responseText[0] == "{")
        err = JSON.parse(xhr.responseText).message;
    alert(err);
}

//showing spinner
function BtnLoading(elem) {
    $(elem).attr("data-original-text", $(elem).html());
    $(elem).prop("disabled", true);
    $(elem).html('<i class="spinner-border spinner-border-sm"></i> Loading...');
}

//removing spinner
function BtnReset(elem) {
    $(elem).prop("disabled", false);
    $(elem).html($(elem).attr("data-original-text"));
}

$(document).ready(function() {
    $("#portfolioWaitingAlert").hide() //remove alert
    $("#forecastWaitingAlert").hide() //remove alert

    $("#getForecastButton").click(getAndShowForecastsByIndexId);
    $("#getPortfolioButton").click(getAndShowOptimalPortfolio);
    $("#getForecastButton").click(function() {
        $("#forecastWaitingAlert").show('medium');
        BtnLoading($(this));
    });
    $("#getPortfolioButton").click(function() {
        $("#portfolioWaitingAlert").show('medium');
        BtnLoading($(this));
    });

});

function showForecastedSeries(res) {
    showForecastedSeriesTextually(res.text);
    showForecastedSeriesGraphically(res.img);
    //possibly validation (metrics too)
    $("#forecastRow").show();
}

function showForecastedSeriesTextually(seriesObject) {
    //series is an object of (date, price) pairs
    $("#textualForecast").html(fromJsonObjectToLis(seriesObject));
}

function showForecastedSeriesGraphically(seriesImageAsJson) {
    $("#graphicForecast").attr('src', fromJsonImageToSrcAttribute(seriesImageAsJson));
}

function showOptimalPortfolio(portfolio) {
    $("#portfolio .content").html(fromJsonObjectToLis(portfolio));
    $("#optimizationRow").show();
}












//utility-functions
function fromJsonToImage(base64imagestring) {
    var basestr64 = base64imagestring;
    basestr64 = basestr64.substring(0, basestr64.length - 1);
    basestr64 = basestr64.substring(2, basestr64.length);
    //imgElem.setAttribute('src', "data:image/png;base64," + baseStr64);
    var image = new Image();
    image.src = 'data:image/png;base64,' + basestr64;
    //document.body.appendChild(image);
    return image;
}

function fromJsonImageToSrcAttribute(base64imagestring) {
    var basestr64 = base64imagestring;
    return 'data:image/png;base64,' + basestr64;
}

function fromArrayToBrSeparatedString(aArray) {
    return fromArrayToPrePostfixedItemsString(aArray, '', '<br>')
}

function fromArrayToLis(aArray) {
    return fromArrayToPrePostfixedItemsString(aArray, '<li>', '</li>');
}

//perfect for currying
function fromArrayToPrePostfixedItemsString(aArray, pre, post) {
    let text = "";
    for (element of aArray) {
        text += pre + element + post;
    }
    return text;
}

function fromJsonObjectToLis(jsonObj) {
    return fromJsonObjectToPrePostfixedItemsString(jsonObj, '<li>', '</li>');
}

function fromJsonObjectToPrePostfixedItemsString(jsonObj, pre, post) {
    let text = "";
    for (var key in jsonObj) {
        text += pre + key + " : " + jsonObj[key] + post;
    }
    return text;
}




/*
old of prof:
 
function showResult(res) {
    document.getElementById("txtarea").value += res.text;
    fromJsonToImage(res.img);
}*/