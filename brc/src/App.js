import React from 'react'

export default function BRC() {
  return (
    <>
      <div>BRC</div>
      <div style={{backgroundColor: "rgb(199, 199, 199)",margin: "6% 15% 6% 15%",padding: "3.5%", alignItems: "center"}}>
        <div style={{display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "center", gap: "4%"}}>
            <h1>See logs below</h1>
            <label for="saving_on"></label>
            <select class = "select-body" name="saving_on" id="saving_on">
                <option value="cloud">Save On</option>
                <option value="cloud">Cloud</option>              
                <option value="local storage">Local Storage</option>
                
            </select>            
            <label for="database"></label>
            <select class="select-body" name="saving_on" id="saving_on">
                <option value="cloud">Select database</option>
                <option value="cloud">MySQL</option>  
                <option value="cloud">SQL lite3</option>             
                <option value="local storage">MongoDB</option>
            </select>
        </div>
        <div style={{backgroundColor: "grey"}}>
            <div style={{display: "inline-block", blockSize: "200px", width: "60%"}}>               
            </div>
        </div>
        <div style={{display: "flex", flexDirection: "row", justifyContent: "space-between", padding: "2%"}}>
            <button style={{padding: "2% 4% 1% 4%", backgroundColor: "rgb(255, 98, 42)", border: "none", borderRadius: "3px", color: "aliceblue"}}>Apply Encryption</button>
            <select class="select-body">
                <option value="cloud">Encryption Type</option>
                <option value="cloud">RSA</option>
                <option value="IBM">SHA 256</option>
                <option value="local storage">SHA 1</option>
                <option value="drive">None</option>
            </select>
        </div>
        <div style={{justifyContent: "center"}}>
            <button style={{alignSelf: "center", marginLeft: "37%",
                            border: "none",
                            borderRadius: "8px",
                            backgroundColor: "blue",
                            color: "antiquewhite",
                            padding: "3%"}}>Convert backup into other database</button>
        </div>
        <div style={{margin: "3.5%", display: "flex", flexDirection: "row", gap: "15%", justifyContent: "center"}}>
            <button style={{backgroundColor: "rgb(79, 182, 251)",
                           border: "none",
                           borderRadius: "6px",
                           padding: "4% 6% 4% 6%"}}>Restore</button>
            <button style={{backgroundColor: "rgb(79, 182, 251)",
                            border: "none",
                            borderRadius: "6px",
                            padding: "4% 6% 4% 6%"}}>Backup</button>
            <button style={{backgroundColor: "rgb(79, 182, 251)",
                            border: "none",
                            borderRadius: "6px",
                            padding: "4% 6% 4% 6%"}}>Restore</button>
        </div>
    </div>
    </>
  )
}

