

// // Restricts input for the given textbox to the given inputFilter function.
// function setInputFilter(textbox, inputFilter, errMsg) {
//     [ "input", "keydown", "keyup", "mousedown", "mouseup", "select", "contextmenu", "drop", "focusout" ].forEach(function(event) {
//       textbox.addEventListener(event, function(e) {
//         if (inputFilter(this.value)) {
//           // Accepted value.
//           if ([ "keydown", "mousedown", "focusout" ].indexOf(e.type) >= 0){
//             this.classList.remove("input-error");
//             this.setCustomValidity("");
//           }
  
//           this.oldValue = this.value;
//           this.oldSelectionStart = this.selectionStart;
//           this.oldSelectionEnd = this.selectionEnd;
//         }
//         else if (this.hasOwnProperty("oldValue")) {
//           // Rejected value: restore the previous one.
//           this.classList.add("input-error");
//           this.setCustomValidity(errMsg);
//           this.reportValidity();
//           this.value = this.oldValue;
//           this.setSelectionRange(this.oldSelectionStart, this.oldSelectionEnd);
//         }
//         else {
//           // Rejected value: nothing to restore.
//           this.value = "";
//         }
//       });
//     });
//   }


/**
 * Monta uma template (toast) para exibir as mensagens do sistema 
 * 
 */
function setMessage(message, color) {     
   html = `<div class="toast align-items-center mb-2 text-white bg-${color} border-0" role="alert" aria-live="assertive" aria-atomic="true">
              <div class="d-flex">
                <div class="toast-body">
                  ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
              </div>
           </div>`  
    let message_alert = document.getElementById("message-alert");     
    message_alert.innerHTML = html;   
   $('.toast').toast('show');
}
   


/**
 * Exibe/oculta spinner quando o ajax é chamado
 * 
 */
function spinner(show = true) {
  if (show) {
    document.querySelector('.loading').classList.remove("d-none");
  }
  else {
    document.querySelector('.loading').classList.add("d-none");
  }
}


// var popover = new bootstrap.Popover(document.querySelector('.popover-dismiss'), {
//   trigger: 'focus'
// })

 
const uuid4 = () => {
  const ho = (n, p) => n.toString(16).padStart(p, 0); /// Return the hexadecimal text representation of number `n`, padded with zeroes to be of length `p`; e.g. `ho(13, 2)` returns `"0d"`
  const data = crypto.getRandomValues(new Uint8Array(16)); /// Fill a buffer with random bits
  data[6] = (data[6] & 0xf) | 0x40; /// Patch the 6th byte to reflect a version 4 UUID
  data[8] = (data[8] & 0x3f) | 0x80; /// Patch the 8th byte to reflect a variant 1 UUID (version 4 UUIDs are)
  const view = new DataView(data.buffer); /// Create a view backed by the 16-byte buffer
  return `${ho(view.getUint32(0), 8)}-${ho(view.getUint16(4), 4)}-${ho(view.getUint16(6), 4)}-${ho(view.getUint16(8), 4)}-${ho(view.getUint32(10), 8)}${ho(view.getUint16(14), 4)}`; /// Compile the canonical textual form from the array data
};


/**
 * 
 * @param  02/03/2018 00:00:00
 * @returns 
 */
function date_convert(date) {
  date = date.trim()
  if (date.indexOf('/') >= 0)  
    date = date.split(" ")[0].split("/").reverse().join('-');
  else 
    date = date.split(" ")[0].split("-").reverse().join('/');
  return date
  
  
}