(function () {
    'use strict';

    var COOKIE_NAME = 'trivia.name';
    var COOKIE_ANSWER = 'trivia.answer';

    var name = Cookies.get(COOKIE_NAME);
    var lastAnswer = Cookies.getJSON(COOKIE_ANSWER) || {};

    var body = $('body');
    var form = $('#form');
    var nameContent = $('#content-name');
    var questionContent = $('#content-question');
    var logoutLink = $('#link-logout');

    var lastQuestion = {};

    logoutLink.click(function (event) {
        event.preventDefault();
        Cookies.remove(COOKIE_NAME);
        location.reload();
    });

    if (name) {
        initializeGame();
    } else {
        nameContent.show();
        form.on('submit', function (event) {
            event.preventDefault();
            Cookies.set(COOKIE_NAME, name = $('#input-name').val());
            initializeGame();
        });
    }

    function initializeGame() {
        nameContent.hide();
        logoutLink.text('Logout ' + name);

        return fetchQuestion().then(function (question) {
            var interval;

            if (lastAnswer.question_id === question.id && null === lastAnswer.is_correct) {
                interval = setInterval(fetchAnswer, 1000);
                fetchAnswer();
            } else {
                interval = setInterval(fetchQuestion, 1000);
                questionContent.on('change', 'input', onQuestionInputChange);
            }

            function fetchAnswer() {
                $.getJSON('answer/' + lastAnswer.id).then(function (response) {
                    lastAnswer.is_correct = response.is_correct;

                    if (null === lastAnswer.is_correct) {
                        return;
                    }

                    clearInterval(interval);
                    initializeGame();
                });
            }

            function onQuestionInputChange(event) {
                event.preventDefault();
                clearInterval(interval);

                lastAnswer = {
                    question_id: question.id,
                    user: name,
                    value: $(this).val(),
                    is_correct: null
                };

                $.post('answer', lastAnswer, function (data) {
                    lastAnswer.id = data.id;
                    Cookies.set(COOKIE_ANSWER, lastAnswer);
                    renderQuestion(question, true);
                    questionContent.off('change', 'input', onQuestionInputChange);
                    initializeGame();
                }, 'json');
            }
        });
    }

    function fetchQuestion() {
        return $.getJSON('question').then(function (question) {
            renderQuestion(question);
            return question;
        });
    }

    function renderQuestion(question, force) {
        var hasAnswered = question.id === lastAnswer.question_id;

        if (hasAnswered && null !== lastAnswer.is_correct) {
            body.addClass(lastAnswer.is_correct ? 'is-correct' : 'is-incorrect');
        } else {
            body.removeClass('is-correct is-incorrect');
        }

        if (!force && lastQuestion.id === question.id) {
            return;
        }

        lastQuestion = question;

        var optionsHtml = question.options.reduce(function (result, option) {
            var isSelected = hasAnswered && option === lastAnswer.value;

            return result + '<label class="form-option' + (isSelected ? ' is-selected' : '') + '">' +
                '<input type="radio" name="answer" value="' + option + '"' +
                (hasAnswered ? ' disabled' : '') +
                (isSelected ? ' checked' : '') +
                '> ' + option + '</label>';
        }, '');

        questionContent.html('<h1>' + question.text + '</h1>' + optionsHtml);
    }

})();
