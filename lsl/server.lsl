//////////////////////////////
//isInteger///////////////////
//test string is valid integer
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

//////////////////////////////
//lineLimit///////////////////
//returns half of free memory
//limit http response body size
integer lineLimit()
{
	return llGetFreeMemory()/2;
}

//////////////////////////////
//processRequest//////////////
//process all incoming http requests
processRequest(key request_id, string method, string path, list data, list query)
{
	if (method == "GET" && path == "/info" && llGetListLength(data) == 0)
	{//linkset info
		integer ln = 0;
		if (llGetLinkNumber())
			ln = LINK_ROOT;
		list details = llGetObjectDetails(llGetLinkKey(ln),
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
		integer i;
		for (i=0;i<5;i++)
			details += [llGetObjectPermMask(i)];
		llHTTPResponse(request_id, 200, llDumpList2String(details, "¦"));
	}
	else if (method == "GET" && llGetSubString(path, 0, 5) == "/prims" && llGetListLength(data) == 0)
	{//return list of all prims
		integer i = 1;
		integer n = llGetNumberOfPrims();
		// if have num argument, start processing from this prim
		if (isInteger(llGetSubString(path, 7, -1)))
			i = (integer)llGetSubString(path, 7, -1);
		if (!llGetLinkNumber()) {i=0;n=0;}
		integer len = 0;
		string resp = "";
		for (;i<=n;i++)
		{
			list pd = llGetObjectDetails(llGetLinkKey(i),
				[
					OBJECT_CREATOR,
					OBJECT_NAME,
					OBJECT_DESC,
					OBJECT_CREATION_TIME
				]);
			pd += [llGetLinkNumberOfSides(i)];
			string line = llDumpList2String(pd, "¦");
			integer lineLen = llStringLength(line) + 3;
			if (len + lineLen + 2 > lineLimit())
			{//memory limit reached, finish adding to response body
				llHTTPResponse(request_id, 200, resp + "\n+");
				return;
			}
			else
			{
				if (len)
				{//not first in body, add delimiter
					resp += "\n";
					len++;
				}
				resp += line;
				len += lineLen;
			}
		}
		llHTTPResponse(request_id, 200, resp);
	}
	else if (method == "GET" && llGetSubString(path, 0, 16) == "/linksetdata/keys"
			&& llGetListLength(data) == 0)
	{//return list of all linkset data keys
		integer i = 0;
		// if have num argument, start processing from this key
		if (isInteger(llGetSubString(path, 18, -1)))
			i = (integer)llGetSubString(path, 18, -1);
		integer len = 0;
		string resp = "";
		list keys = llLinksetDataListKeys(i, -1);
		integer n;
		for(n=0;n<llGetListLength(keys);n++)
		{
			string line = llList2String(keys, n);
			integer lineLen = llStringLength(line) + 1;
			if (len + lineLen + 2 > lineLimit()/2)
			{//memory limit reached, finish adding to response body
				llHTTPResponse(request_id, 200, resp + "¦+");
				return;
			}
			else
			{
				if (len)
				{//not first in body, add delimiter
					resp += "¦";
					len++;
				}
				resp += line;
				len += lineLen;
			}
		}
		llHTTPResponse(request_id, 200, resp);
	}
	else if (method == "GET" && llGetSubString(path, 0, 17) == "/linksetdata/read/"
			&& llStringLength(path) > 17 && llGetListLength(data) == 0)
	{//read linkset data value by name
		string name = llGetSubString(path, 18, -1);
		llHTTPResponse(request_id, 200, llLinksetDataRead(name));
	}
	else if (method == "POST" && llGetSubString(path, 0, 17) == "/linksetdata/read/"
			&& llStringLength(path) > 17 && llGetListLength(data) == 1)
	{//read protected linkset data value by name
		string name = llGetSubString(path, 18, -1);
		string pass = llList2String(data, 0);
		llHTTPResponse(request_id, 200, llLinksetDataReadProtected(name, pass));
	}
	else if (method == "POST" && llGetSubString(path, 0, 18) == "/linksetdata/write/"
			&& llStringLength(path) > 18 && llGetListLength(data) == 1)
	{//write linkset data value
		string name = llGetSubString(path, 19, -1);
		string value = llList2String(data, 0);
		llHTTPResponse(request_id, 200, (string)llLinksetDataWrite(name, value));
	}
	else if (method == "POST" && llGetSubString(path, 0, 18) == "/linksetdata/write/"
			&& llStringLength(path) > 18 && llGetListLength(data) == 2)
	{//write protected linkset data value
		string name = llGetSubString(path, 19, -1);
		string value = llList2String(data, 0);
		string pass = llList2String(data, 1);
		llHTTPResponse(request_id, 200, (string)llLinksetDataWriteProtected(name, value, pass));
	}
	else if (method == "POST" && llGetSubString(path, 0, 19) == "/linksetdata/delete/"
			&& llStringLength(path) > 19 && llGetListLength(data) == 0)
	{//delete linkset data value by name
		string name = llGetSubString(path, 20, -1);
		llHTTPResponse(request_id, 200, (string)llLinksetDataDelete(name));
	}
	else if (method == "POST" && llGetSubString(path, 0, 19) == "/linksetdata/delete/"
			&& llStringLength(path) > 19 && llGetListLength(data) == 1)
	{//delete protected linkset data value by name
		string name = llGetSubString(path, 20, -1);
		string pass = llList2String(data, 0);
		llHTTPResponse(request_id, 200, (string)llLinksetDataDeleteProtected(name, pass));
	}
	else if (method == "GET" && llGetSubString(path, 0, 14) == "/inventory/read"
			&& llGetListLength(data) == 0)
	{//get inventory
		integer i = 0;
		integer type = INVENTORY_ALL;
		if (llGetListLength(query) == 2 && llList2String(query, 0) == "type"
			&& isInteger(llList2String(query, 1)))
		{
			integer it = (integer)llList2String(query, 1);
			if (llListFindList([INVENTORY_TEXTURE, INVENTORY_SOUND, INVENTORY_LANDMARK,
								INVENTORY_CLOTHING, INVENTORY_OBJECT, INVENTORY_NOTECARD,
								INVENTORY_SCRIPT, INVENTORY_BODYPART, INVENTORY_ANIMATION,
								INVENTORY_GESTURE, INVENTORY_SETTING, INVENTORY_MATERIAL],
								[it]) != -1)
				type = it;
		}
		// if have num argument, start processing from this key
		if (isInteger(llGetSubString(path, 16, -1)))
		{
			i = (integer)llGetSubString(path, 16, -1);
		}
		integer len = 0;
		string resp = "";
		for (;i<llGetInventoryNumber(type);i++)
		{
			string name = llGetInventoryName(type, i);
			list details = [llGetInventoryKey(name),
							llGetInventoryType(name),
							name,
							llGetInventoryDesc(name),
							llGetInventoryCreator(name),
							llGetInventoryPermMask(name, MASK_BASE),
							llGetInventoryPermMask(name, MASK_OWNER),
							llGetInventoryPermMask(name, MASK_GROUP),
							llGetInventoryPermMask(name, MASK_EVERYONE),
							llGetInventoryPermMask(name, MASK_NEXT),
							llGetInventoryAcquireTime(name)];
			string line = llDumpList2String(details, "¦");
			integer lineLen = llStringLength(line) + 10;
			if (len + lineLen + 2 > lineLimit())
			{//memory limit reached, finish adding to response body
				llHTTPResponse(request_id, 200, resp + "\n+");
				return;
			}
			else
			{
				if (len)
				{//not first in body, add delimiter
					resp += "\n";
					len++;
				}
				resp += line;
				len += lineLen;
			}
		}
		llHTTPResponse(request_id, 200, resp);
	}
	else if (method == "POST" && llGetSubString(path, 0, -1) == "/inventory/delete" && llGetListLength(data))
	{
		integer i;
		for (i=0;i<llGetListLength(data);i++)
			if (llGetInventoryType(llList2String(data, i)) == -1)
			{
				llHTTPResponse(request_id, 422, "'" + llList2String(data, i) + "' not found");
				return;
			}
		for (i=0;i<llGetListLength(data);i++)
			llRemoveInventory(llList2String(data, i));
		llHTTPResponse(request_id, 200, "Ok");
	}
	else if (method == "POST" && llGetSubString(path, 0, -1) == "/inventory/give"
				&& llGetListLength(data) == 2)
	{
		if (llGetInventoryType(llList2String(data, 1)) == -1)
		{
			llHTTPResponse(request_id, 422, "'" + llList2String(data, 1) + "' not found");
			return;
		}
		if (!(llGetInventoryPermMask(llList2String(data, 1), MASK_OWNER) & PERM_TRANSFER))
		{
			llHTTPResponse(request_id, 403, "'" + llList2String(data, 1) + "' not transfer permission");
			return;
		}
		if (llList2String(data, 0) == NULL_KEY)
		{
			llHTTPResponse(request_id, 400,
							"'" + llList2String(data, 1) + "' Can't give inventory to NULL_KEY");
			return;
		}
		llGiveInventory(llList2String(data, 0), llList2String(data, 1));
		llHTTPResponse(request_id, 200, "Ok");
	}
	else if (method == "POST" && llGetSubString(path, 0, -1) == "/inventory/givelist"
				&& llGetListLength(data) > 2)
	{
		integer i;
		if (llGetListLength(data) > 43)
		{
			llHTTPResponse(request_id, 413,
							"'" + llList2String(data, 0) + "' No more than 41 items");
			return;
		}
		if (!llGetListLength(llGetObjectDetails(llList2String(data, 0), [OBJECT_NAME])))
		{
			llHTTPResponse(request_id, 400,
							"'" + llList2String(data, 0) + "' Destination must be in same region");
			return;
		}
		for (i=2;i<llGetListLength(data);i++)
		{
			if (llGetInventoryType(llList2String(data, i)) == -1)
			{
				llHTTPResponse(request_id, 422, "'" + llList2String(data, i) + "' not found");
				return;
			}
			if (!(llGetInventoryPermMask(llList2String(data, i), MASK_OWNER) & PERM_TRANSFER))
			{
				llHTTPResponse(request_id, 403, "'" + llList2String(data, i) + "' not transfer permission");
				return;
			}
		}
		llGiveInventoryList(llList2String(data, 0), llList2String(data, 1), llList2List(data, 2, -1));
		llHTTPResponse(request_id, 200, "Ok");
	}
	else//unknown request
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
			// string query = llGetHTTPHeader(request_id, "x-query-string");
			//a0=v0&a1=v1
			list query;
			list querystring = llParseString2List(llGetHTTPHeader(request_id, "x-query-string"), ["&"], []);
			integer i;
			for (i=0;i<llGetListLength(querystring);i++)
			{
				list lst = llParseString2List(llList2String(querystring, i), ["="], []);
				if (llGetListLength(lst) == 2)
					query += lst;
			}
			llOwnerSay(path + " - " + method + ", args: '" + llList2CSV(query) + "': \n" + body);
			list data = llParseString2List(body, ["¦"], []);
			processRequest(request_id, method, path, data, query);
			integer iFM = llGetFreeMemory();
			integer iUM = llGetUsedMemory();
			llOwnerSay("Used mem: " +(string)iUM + " Free mem: " + (string)iFM
						+ " Garb mem: " + (string)(llGetMemoryLimit()-iFM-iUM));
		}
	}
}
