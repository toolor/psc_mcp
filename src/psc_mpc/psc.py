"""
普通话水平测试 (PSC) 报名查询工具

该模块提供了一个用于查询普通话水平测试报名信息的工具，包括:
- 查询支持报名的省份列表
- 查询各省当前开放报名的测试站点
- 查询各省即将开放报名的测试站点
- 统计信息查询

依赖的 API 接口:
- https://psc.urabas.com/psc/api/provinces - 获取省份列表
- https://psc.urabas.com/psc/api/stations/open - 获取开放报名的测试站点
- https://psc.urabas.com/psc/api/stations/next - 获取即将开放报名的测试站点
"""

import sys
import json
from typing import Optional
from datetime import datetime

import requests
from fastmcp import FastMCP

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

mcp = FastMCP("普通话水平测试报名查询工具",
   instructions="""
       普通话查询工具，
        调用 get_provinces() 获取省份列表。
        每次调用都需要重新获取省份列表，因为省份数据可能会变化。
        province_id 为省份的唯一标识符，例如 "ningxia"。这个数据从 get_provinces() 返回的列表中获取。
        调用 get_open_stations(province_id) 获取指定省份的开放报名测试站点。
        调用 get_next_stations(province_id) 获取指定省份即将开放报名的测试站点。
        调用 get_exam_info(province_id, exam_type) 获取更详细的考试信息。

    """)

def fetch_data(url: str, params: Optional[dict] = None) -> dict:
    """
    从 API 获取数据的辅助函数，包含错误处理机制
    
    Args:
        url (str): 要请求的 API 地址
        params (dict, optional): URL 参数
        
    Returns:
        dict: API 返回的 JSON 数据，失败时返回错误信息字典
        
    Raises:
        不抛出异常，而是返回包含错误信息的字典
    """
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        if not response.headers.get('Content-Type', '').startswith('application/json'):
            raise ValueError(f"API 返回非 JSON 格式数据：{response.headers.get('Content-Type')}")
        
        data = response.json()
        return data
    except requests.exceptions.Timeout:
        return {"code": 504, "data": [], "message": "API 请求超时"}
    except requests.exceptions.HTTPError as e:
        return {"code": e.response.status_code if e.response else 500, "data": [], "message": f"HTTP 错误：{str(e)}"}
    except ValueError as e:
        return {"code": 400, "data": [], "message": str(e)}
    except Exception as e:
        return {"code": 500, "data": [], "message": f"API 请求失败：{str(e)}"}


def get_provinces() -> list:
    """
    获取省份列表的辅助函数，统一数据格式
    
    Returns:
        list: 省份数据列表，每个元素为包含省份信息的字典
    """
    provinces_resp = fetch_data("https://psc.urabas.com/psc/api/provinces")
    provinces = []
    if isinstance(provinces_resp, dict):
        provinces = provinces_resp.get("data") or []
        if not isinstance(provinces, list):
            provinces = []
    elif isinstance(provinces_resp, list):
        provinces = provinces_resp
    
    return provinces


@mcp.resource("psc://provinces")
def get_provinces_resource() -> str:
    """
    获取省份列表资源
    
    Returns:
        str: JSON 格式的省份列表数据
    """
    provinces = get_provinces()
    
    return json.dumps({
        "code": 200,
        "data": provinces,
        "message": "成功",
        "count": len(provinces)
    }, ensure_ascii=False, indent=2)


@mcp.resource("psc://psc/open")
def get_open_psc_resource() -> str:
    """
    获取所有正在报名的考试资源
    
    Returns:
        str: JSON 格式的正在报名考试数据
    """
    provinces = get_provinces()
    open_tests = []
    
    for province in provinces:
        province_name = province.get("provinceName") or province.get("name")
        province_id = province.get("provinceId") or province.get("url")
        
        if not province_id or not province_name:
            continue
        
        open_resp = fetch_data("https://psc.urabas.com/psc/api/stations/open", {"provinceId": province_id})
        open_data = open_resp.get("data") if isinstance(open_resp, dict) else open_resp
        open_data = open_data or []
        
        if isinstance(open_data, list):
            for station in open_data:
                station_org_name = station.get("orgName") or station.get("org_name")
                station_city = station.get("city")
                test_list = station.get("bmTestTaskDtoList") or []
                
                if isinstance(test_list, list):
                    for test in test_list:
                        test["province"] = province_name
                        if station_org_name:
                            test["orgName"] = station_org_name
                        if station_city:
                            test["city"] = station_city
                        open_tests.append(test)
    
    return json.dumps({
        "code": 200,
        "data": open_tests,
        "message": "成功",
        "count": len(open_tests)
    }, ensure_ascii=False, indent=2)


@mcp.resource("psc://psc/next")
def get_next_psc_resource() -> str:
    """
    获取所有即将报名的考试资源
    
    Returns:
        str: JSON 格式的即将报名考试数据
    """
    provinces = get_provinces()
    next_tests = []
    
    for province in provinces:
        province_name = province.get("provinceName") or province.get("name")
        province_id = province.get("provinceId") or province.get("url")
        
        if not province_id or not province_name:
            continue
        
        next_resp = fetch_data("https://psc.urabas.com/psc/api/stations/next", {"provinceId": province_id})
        next_data = next_resp.get("data") if isinstance(next_resp, dict) else next_resp
        next_data = next_data or []
        
        if isinstance(next_data, list):
            for station in next_data:
                station_org_name = station.get("orgName") or station.get("org_name")
                station_city = station.get("city")
                test_list = station.get("bmTestTaskDtoList") or []
                
                if isinstance(test_list, list):
                    for test in test_list:
                        test["province"] = province_name
                        if station_org_name:
                            test["orgName"] = station_org_name
                        if station_city:
                            test["city"] = station_city
                        next_tests.append(test)
    
    return json.dumps({
        "code": 200,
        "data": next_tests,
        "message": "成功",
        "count": len(next_tests)
    }, ensure_ascii=False, indent=2)


@mcp.resource("psc://stats")
def get_stats_resource() -> str:
    """
    获取统计信息资源
    
    Returns:
        str: JSON 格式的统计数据
    """
    provinces = get_provinces()
    open_tests = []
    next_tests = []
    
    for province in provinces:
        province_name = province.get("provinceName") or province.get("name")
        province_id = province.get("provinceId") or province.get("url")
        
        if not province_id or not province_name:
            continue
        
        open_resp = fetch_data("https://psc.urabas.com/psc/api/stations/open", {"provinceId": province_id})
        open_data = open_resp.get("data") if isinstance(open_resp, dict) else open_resp
        open_data = open_data or []
        
        if isinstance(open_data, list):
            for station in open_data:
                test_list = station.get("bmTestTaskDtoList") or []
                if isinstance(test_list, list):
                    for test in test_list:
                        test["province"] = province_name
                        open_tests.append(test)
        
        next_resp = fetch_data("https://psc.urabas.com/psc/api/stations/next", {"provinceId": province_id})
        next_data = next_resp.get("data") if isinstance(next_resp, dict) else next_resp
        next_data = next_data or []
        
        if isinstance(next_data, list):
            for station in next_data:
                test_list = station.get("bmTestTaskDtoList") or []
                if isinstance(test_list, list):
                    for test in test_list:
                        test["province"] = province_name
                        next_tests.append(test)
    
    stats = {
        "code": 200,
        "data": {
            "timestamp": datetime.now().isoformat(),
            "open_psc": {
                "total": len(open_tests),
                "provinces": len({test.get("province") for test in open_tests if test.get("province")})
            },
            "next_psc": {
                "total": len(next_tests),
                "provinces": len({test.get("province") for test in next_tests if test.get("province")})
            }
        },
        "message": "成功"
    }
    
    return json.dumps(stats, ensure_ascii=False, indent=2)


@mcp.tool
def get_provinces_tool() -> dict:
    """
    获取省份列表
    
    从 API 获取支持普通话水平测试报名的所有省份列表
    
    Returns:
        dict: JSON 格式的省份列表数据
    """
    try:
        provinces = get_provinces()
        return {
            "code": 200,
            "data": provinces,
            "message": "成功",
            "count": len(provinces)
        }
    except Exception as e:
        return {
            "code": 500,
            "data": [],
            "message": str(e)
        }


@mcp.tool
def get_open_stations(province_id: str) -> dict:
    """
    获取指定省份当前开放报名的测试站点
    
    Args:
        province_id (str): 省份 ID
        
    Returns:
        dict: JSON 格式的开放报名测试站点数据
    """
    try:
        url = f"https://psc.urabas.com/psc/api/stations/open?provinceId={province_id}"
        stations_data = fetch_data(url)
        return {
            "code": 200,
            "data": stations_data.get("data") if isinstance(stations_data, dict) else stations_data,
            "message": "成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": [],
            "message": str(e)
        }


@mcp.tool
def get_next_stations(province_id: str) -> dict:
    """
    获取指定省份即将开放报名的测试站点
    
    Args:
        province_id (str): 省份 ID
        
    Returns:
        dict: JSON 格式的即将开放报名测试站点数据
    """
    try:
        url = f"https://psc.urabas.com/psc/api/stations/next?provinceId={province_id}"
        stations_data = fetch_data(url)
        return {
            "code": 200,
            "data": stations_data.get("data") if isinstance(stations_data, dict) else stations_data,
            "message": "成功"
        }
    except Exception as e:
        return {
            "code": 500,
            "data": [],
            "message": str(e)
        }


@mcp.tool()
def get_exam_info(province_id: Optional[str] = None, exam_type: str = "all") -> dict:
    """获取普通话考试信息。
    
    ⚠️ 重要：省份 ID 必须从 get_provinces_tool() 接口获取，或从 psc://provinces 资源获取。
    只有 https://psc.urabas.com/psc/api/provinces 返回的省份才支持报名。
    
    特殊说明：查询"新疆"时会同时返回新疆和新疆兵团的结果，并分开显示。
    ⚠️ 建议：优先查询具体省份，避免查询全国（32 个省份）导致响应缓慢。
    
    Args:
        province_id: 省份 ID，如"jiangsu"。必须从省份列表接口获取，不提供则获取全国数据
        exam_type: 考试类型，"open"(正在报名), "next"(即将报名), 或"all"(全部)
    
    Returns:
        包含考试信息的字典，新疆地区会分开显示新疆和新疆兵团
    """
    provinces = get_provinces()
    
    if not province_id:
        province_names = [p.get("provinceName") for p in provinces if p.get("provinceName")]
        return {
            "code": 200,
            "data": {
                "message": "⚠️ 全国包含 32 个省份，查询所有省份可能导致响应缓慢。",
                "suggestion": "建议先使用 get_provinces_tool() 获取省份列表，然后查询具体省份。",
                "available_provinces": province_names,
                "example": "get_exam_info(province_id='jiangsu', exam_type='open') 查询江苏省"
            },
            "message": "请使用具体省份 ID 查询，避免查询全国数据"
        }
    
    target_provinces = []
    
    if province_id:
        for province in provinces:
            pid = province.get("provinceId") or province.get("url")
            pname = province.get("provinceName") or province.get("name")
            
            if pid == province_id:
                target_provinces.append(province)
                break
            elif province_id == "xinjiang" and pid in ["xinjiang", "xinjiangbingtuan"]:
                target_provinces.append(province)
            elif province_id == "xinjiangbingtuan" and pid == "xinjiangbingtuan":
                target_provinces.append(province)
                break
    else:
        target_provinces = provinces
    
    if not target_provinces:
        return {
            "code": 404,
            "data": [],
            "message": f"未找到省份：{province_id}。请使用 get_provinces_tool() 获取正确的省份 ID。"
        }
    
    all_open = []
    all_next = []
    province_results = {}
    
    for province in target_provinces:
        province_name = province.get("provinceName") or province.get("name")
        province_id_val = province.get("provinceId") or province.get("url")
        
        if not province_id_val or not province_name:
            continue
        
        province_open = []
        province_next = []
        
        if exam_type in ["open", "all"]:
            open_resp = fetch_data("https://psc.urabas.com/psc/api/stations/open", {"provinceId": province_id_val})
            open_data = open_resp.get("data") if isinstance(open_resp, dict) else open_resp
            if isinstance(open_data, list):
                for station in open_data:
                    test_list = station.get("bmTestTaskDtoList") or []
                    if isinstance(test_list, list):
                        for test in test_list:
                            test["province"] = province_name
                            test["provinceId"] = province_id_val
                            province_open.append(test)
                            all_open.append(test)
        
        if exam_type in ["next", "all"]:
            next_resp = fetch_data("https://psc.urabas.com/psc/api/stations/next", {"provinceId": province_id_val})
            next_data = next_resp.get("data") if isinstance(next_resp, dict) else next_resp
            if isinstance(next_data, list):
                for station in next_data:
                    test_list = station.get("bmTestTaskDtoList") or []
                    if isinstance(test_list, list):
                        for test in test_list:
                            test["province"] = province_name
                            test["provinceId"] = province_id_val
                            province_next.append(test)
                            all_next.append(test)
        
        province_results[province_name] = {
            "provinceId": province_id_val,
            "open": province_open,
            "next": province_next
        }
    
    result_data = {
        "exam_type": exam_type,
        "total_open": len(all_open),
        "total_next": len(all_next)
    }
    
    if province_id and len(target_provinces) == 1:
        province_name = target_provinces[0].get("provinceName") or target_provinces[0].get("name")
        result_data.update(province_results[province_name])
    else:
        result_data["provinces"] = province_results
        result_data["open"] = all_open
        result_data["next"] = all_next
    
    if exam_type == "open":
        if province_id and len(target_provinces) == 1:
            result_data = {"open": result_data.get("open", [])}
        else:
            result_data = {"open": all_open}
    elif exam_type == "next":
        if province_id and len(target_provinces) == 1:
            result_data = {"next": result_data.get("next", [])}
        else:
            result_data = {"next": all_next}
    
    return {
        "code": 200,
        "data": result_data,
        "message": "成功"
    }


def main():
    """主函数，用于启动 PSC MPC 服务"""
    mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")


if __name__ == "__main__":
    main()