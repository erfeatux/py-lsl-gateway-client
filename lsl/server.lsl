integer isInteger(string str)
{
	if (str == "")
		return FALSE;
	integer i;
	integer isnull = TRUE;
	for (i=0;i<llStringLength(str);i++)
	{
		if (llGetSubString(str, i, i) != "0")
		{
			isnull = FALSE;
			i=llStringLength(str);
		}
	}
	if ((integer)str || isnull)
		return TRUE;
	else
		return FALSE;
}

processRequest(key request_id, string method, string path, list data)
{
	if (method == "GET" && path == "/info" && llGetListLength(data) == 0)
	{
		list details = llGetObjectDetails(llGetLinkKey(LINK_ROOT),
			[
				OBJECT_LAST_OWNER_ID,
				OBJECT_CREATOR,
				OBJECT_GROUP,
				OBJECT_DESC,
				OBJECT_ATTACHED_POINT,
				OBJECT_PRIM_COUNT,
				OBJECT_TOTAL_INVENTORY_COUNT,
				OBJECT_CREATION_TIME,
				OBJECT_REZ_TIME
			]);
		details += [llGetScriptName()];
		llHTTPResponse(request_id, 200, llDumpList2String(details, "¦"));
	}
	else if (method == "GET" && llGetSubString(path, 0, 5) == "/prims" && llGetListLength(data) == 0)
	{
		integer i = 1;
		if (isInteger(llGetSubString(path, 7, -1)))
			i = (integer)llGetSubString(path, 7, -1);
		integer len = 0;
		string resp = "";
		for (;i<=llGetNumberOfPrims();i++)
		{
			list pd = llGetObjectDetails(llGetLinkKey(i),
				[
					OBJECT_CREATOR,
					OBJECT_NAME,
					OBJECT_DESC,
					OBJECT_CREATION_TIME
				]);
			string line = llDumpList2String(pd, "¦");
			integer lineLen = llStringLength(line) + 3;
			if (len + lineLen + 2 > 2048)
			{
				llHTTPResponse(request_id, 200, resp + "\n+");
				return;
			}
			else
			{
				if (len)
				{
					resp += "\n";
					len++;
				}
				resp += line;
				len += lineLen;
			}
		}
		llHTTPResponse(request_id, 200, resp);
	}
	else
		llHTTPResponse(request_id, 501, "Not Implemented");
}

default
{
	state_entry()
	{
		integer iFM = llGetFreeMemory();
		integer iUM = llGetUsedMemory();
		llOwnerSay("Used mem: " +(string)iUM + " Free mem: " + (string)iFM
					+ " Garb mem: " + (string)(llGetMemoryLimit()-iFM-iUM));

		llRequestSecureURL();
	}

	http_request(key request_id, string method, string body)
	{
		if (method == URL_REQUEST_GRANTED)
			llOwnerSay(body);
		else if (method == URL_REQUEST_DENIED)
			llOwnerSay("Not url granted");
		else
		{
			string path = llGetHTTPHeader(request_id, "x-path-info");
			llOwnerSay(path + " - " + method + ": \n" + body);
			list data = llParseString2List(body, ["¦"], []);
			processRequest(request_id, method, path, data);
			integer iFM = llGetFreeMemory();
			integer iUM = llGetUsedMemory();
			llOwnerSay("Used mem: " +(string)iUM + " Free mem: " + (string)iFM
						+ " Garb mem: " + (string)(llGetMemoryLimit()-iFM-iUM));
		}
	}
}
