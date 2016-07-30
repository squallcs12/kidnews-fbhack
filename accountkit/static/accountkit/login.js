(function ($) {
  // initialize Account Kit with CSRF protection
  AccountKit_OnInteractive = function(){
    AccountKit.init(
      {
        appId: FACEBOOK_APP_ID,
        state: $.cookie('csrftoken'),
        version: ACCOUNT_KIT_API_VERSION
      }
    );
  };

  // login callback
  function loginCallback(response) {
    console.log(response);
    if (response.status === 'PARTIALLY_AUTHENTICATED') {
      $('#id_code').val(response.code);
      $('#code_form').submit();
    }
    else if (response.status === 'NOT_AUTHENTICATED') {
      // handle authentication failure
    }
    else if (response.status === 'BAD_PARAMS') {
      // handle bad parameters
    }
  }

  $('#code_form').ajaxForm(function (data) {
    location.href = 'https://www.facebook.com/messenger_platform/account_linking' +
                    '?account_linking_token=' + (new URI()).search(true).account_linking_token +
                    '&authorization_code=' + data.key;
  });

  // phone form submission handler
  $('#login_by_phone').click(function (e) {
    e.preventDefault();

    var country_code = $('#country').val();
    var ph_num = $('#phone').val();
    AccountKit.login('PHONE', {countryCode: country_code, phoneNumber: ph_num}, loginCallback);
  });

  // email form submission handler
  $('#login_by_email').click(function (e) {
    e.preventDefault();
    var email_address = $('#email').val();

    AccountKit.login('EMAIL', {emailAddress: email_address}, loginCallback);
  });
})(jQuery)
